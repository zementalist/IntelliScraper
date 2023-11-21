import re
import os
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModel
import unicodedata
from sklearn.model_selection import train_test_split
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
import torch
import torch.nn as nn
from transformers import AdamW, get_linear_schedule_with_warmup
import random
import time
import torch.nn.functional as F

if torch.cuda.is_available():
    device = torch.device('cuda')
    print(f'Using {torch.cuda.device_count()} GPU(s)!')
    print(f'Device name: {torch.cuda.get_device_name(0)}')
else:
    device = torch.device('cpu')
    print('No GPU available.')

def set_seed(seed_value=42):
    random.seed(seed_value)
    np.random.seed(seed_value)
    torch.manual_seed(seed_value)
    torch.cuda.manual_seed_all(seed_value)

def initialize_model(train_dataloader, epochs=4):
  
    bert_classifier = BertClassifier(freeze_bert=False)
    bert_classifier.to(device)
    
    optimizer = AdamW(params=list(bert_classifier.parameters()), lr=5e-5, eps=1e-8)
    
    total_steps = len(train_dataloader) * epochs
    
    schedular = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)
    
    return bert_classifier, optimizer, schedular

class BertClassifier(nn.Module):
    
    def __init__(self, freeze_bert=False):
        
        super(BertClassifier, self).__init__()
        D_in = 256
        H = 50
        D_out = 2
#         D_out = 3
        self.bert = AutoModel.from_pretrained('asafaya/bert-mini-arabic') 
        self.classifier = nn.Sequential(
            nn.Linear(D_in, H),
            nn.ReLU(),
            nn.Dropout(0.9),
            nn.Linear(H, D_out)
        )
        
        if freeze_bert:
            for param in self.bert.parameters():
                param.requires_grad = False
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids,
                            attention_mask=attention_mask)
        last_hidden_state_cls = outputs[0][:, 0, :]
        logits = self.classifier(last_hidden_state_cls)
        
        return logits

class CampaignClassifier:

    def __init__(self, data_path=None):
        if data_path:
          self.df = pd.read_csv(data_path)
        self.batch_size = 16
        self.loss_fn = nn.CrossEntropyLoss()
        self.model_path = 'model-bert-mini.pt'
      
        if os.path.exists(self.model_path):
          self.model = BertClassifier()
          self.model.load_state_dict(torch.load(self.model_path))
          self.model.to(device)
        else:
          self.model = None
        self.sent_length = 100

    def prepare_df(self):
        self.df.drop(columns=['Unnamed: 0'], inplace = True, axis = 1)
        self.df.dropna(inplace=True)
        self.df.drop_duplicates(inplace=True)

        return self.df

    def text_preprocessing_campaign(self, text):
        
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text)
        text = unicodedata.normalize('NFC', text)
        text = re.sub(r'(@.*?)[\s]', ' ', text)
        text = re.sub(r'&amp', '&', text)
        text = re.sub("@\S+", " ", text)
        text = re.sub("#\S+", " ", text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"[a-zA-Z]", '', text)
        text = re.sub('\?|\.|\!|\/|\;|\:|\.', '', text)
        return text
    
    def preprocessing_for_bert(self, data):
    
        input_ids = []
        attention_masks = []
        
        tokenizer = AutoTokenizer.from_pretrained('asafaya/bert-mini-arabic') 

        for i, sent in enumerate(data):
            encoded_sent = tokenizer.encode_plus(
                text=self.text_preprocessing_campaign(sent),
                add_special_tokens=True,
                max_length=self.sent_length,
                padding='max_length',
                return_attention_mask=True,
                truncation=True
                )
            input_ids.append(encoded_sent.get('input_ids'))
            attention_masks.append(encoded_sent.get('attention_mask'))
        input_ids = torch.tensor(input_ids)
        attention_masks = torch.tensor(attention_masks)
        
        return input_ids, attention_masks
    
    def split_data(self):

        X = self.df.descriptions.values
        y = self.df.labels.values

        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify = y)

        train_inputs, train_masks = self.preprocessing_for_bert(X_train)
        val_inputs, val_masks = self.preprocessing_for_bert(X_val)
        train_labels = torch.tensor(y_train).type(torch.LongTensor)
        val_labels = torch.tensor(y_val).type(torch.LongTensor)

        train_data = TensorDataset(train_inputs, train_masks, train_labels)
        train_sampler = RandomSampler(train_data)
        self.train_dataloader= DataLoader(train_data, sampler=train_sampler, batch_size=self.batch_size)

        val_data = TensorDataset(val_inputs, val_masks, val_labels)
        val_sampler = RandomSampler(val_data)
        self.val_dataloader = DataLoader(val_data, sampler=val_sampler, batch_size=self.batch_size)

    def train(self, epochs=4, evaluation=True):
      
        self.df = self.prepare_df()
        self.split_data()
        set_seed(42)
        self.model = None
        self.model, optimizer, scheduler = initialize_model(self.train_dataloader, epochs=2)

        print("Start training...\n")
        for epoch_i in range(epochs):

            print(f"{'Epoch':^7} | {'Batch':^7} | {'Train Loss':^12} | {'Val Loss':^10} | {'Val Acc':^9} | {'Elapsed':^9}")
            print("-"*70)
            
            t0_epoch, t0_batch = time.time(), time.time()
            
            total_loss, batch_loss, batch_counts = 0, 0, 0
            
            self.model.train()
            
            for step, batch in enumerate(self.train_dataloader):
                batch_counts +=1
                b_input_ids, b_attn_mask, b_labels = tuple(t.to(device) for t in batch)
                
                self.model.zero_grad()
                
                logits = self.model(b_input_ids, b_attn_mask)
                
                loss = self.loss_fn(logits, b_labels)
                batch_loss += loss.item()
                total_loss += loss.item()
                
                loss.backward()
                
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                
                optimizer.step()
                scheduler.step()
                
                if (step % 100 == 0 and step != 0) or (step == len(self.train_dataloader) - 1):
                    # Calculate time elapsed for 20 batches
                    time_elapsed = time.time() - t0_batch
                    print(f"{epoch_i + 1:^7} | {step:^7} | {batch_loss / batch_counts:^12.6f} | {'-':^10} | {'-':^9} | {time_elapsed:^9.2f}")
                    
                    batch_loss, batch_counts = 0, 0
                    t0_batch = time.time()
                    
            avg_train_loss = total_loss / len(self.train_dataloader)
            print("-"*70)
            
            if evaluation == True:
                val_loss, val_accuracy = self.evaluate()
                time_elapsed = time.time() - t0_epoch
                print(f"{epoch_i + 1:^7} | {'-':^7} | {avg_train_loss:^12.6f} | {val_loss:^10.6f} | {val_accuracy:^9.2f} | {time_elapsed:^9.2f}")
                print("-"*70)
            print("\n")
        
        print("Training complete!")
        torch.save(self.model.state_dict(), self.model_path)
        
    def evaluate(self):
        self.model.eval()
        
        val_accuracy = []
        val_loss = []
        
        for batch in self.val_dataloader:
            
            b_input_ids, b_attn_mask, b_labels = tuple(t.to(device) for t in batch)
            
            with torch.no_grad():
                logits = self.model(b_input_ids, b_attn_mask)
            
            loss = self.loss_fn(logits, b_labels)
            val_loss.append(loss.item())
            
            preds = torch.argmax(logits, dim=1).flatten()
            
            accuracy = (preds == b_labels).cpu().numpy().mean() * 100
            val_accuracy.append(accuracy)
        
        val_loss = np.mean(val_loss)
        val_accuracy = np.mean(val_accuracy)
        
        return val_loss, val_accuracy
    
    def bert_predict(self, test_dataloader):

        self.model.eval()
        all_logits = []
        
        for batch in test_dataloader:
            
            b_input_ids, b_attn_mask = tuple(t.to(device) for t in batch)[:2]
            
            with torch.no_grad():
                logits = self.model(b_input_ids, b_attn_mask)
                
            all_logits.append(logits)
            
        all_logits = torch.cat(all_logits, dim=0)
        
        props = F.softmax(all_logits, dim=1).cpu().numpy()
        
        return props 
    
    def predict_if_campaign(self, text):

        if not self.model:
          print('Train a model first')
          return 
        
        df = pd.DataFrame([text])
        df = df.rename(columns = {0:"text"})
        print(df.text.values)
        test_inputs, test_masks = self.preprocessing_for_bert(df.text.values)


        test_dataset = TensorDataset(test_inputs, test_masks)
        test_sampler = SequentialSampler(test_dataset)
        test_dataloader = DataLoader(test_dataset, sampler=test_sampler, batch_size=32)

        probs = self.bert_predict(test_dataloader)
        print(probs)

        threshold = 0.5
        preds = np.where(probs[:, 1] > threshold, "positive", "negative")

        return preds
    
def main():
    
    c_classifier = CampaignClassifier('ads_cleaned.csv')
    c_classifier.train()
    print(c_classifier.predict_if_campaign('استمتع بأحدث عروض الصيف معانا'))
    
if __name__ == "__main__":
    main()