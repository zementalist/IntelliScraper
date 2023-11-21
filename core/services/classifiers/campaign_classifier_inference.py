import re
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModel
import unicodedata
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
import torch
import torch.nn as nn
from transformers import AdamW, get_linear_schedule_with_warmup
import random
import torch.nn.functional as F

if torch.cuda.is_available():
    device = torch.device('cuda')
    print(f'Using {torch.cuda.device_count()} GPU(s)!')
    print(f'Device name: {torch.cuda.get_device_name(0)}')
else:
    device = torch.device('cpu')


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

    def __init__(self, model):
        self.model_path = 'model-bert-mini.pt'
      
        self.model = BertClassifier()
        self.model.load_state_dict(model)
        self.model.eval()
        self.sent_length = 100

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

        if isinstance(text, str):
             text = [text]

        if not self.model:
          print('Train a model first')
          return 
        
        df = pd.DataFrame(text)
        df = df.rename(columns = {0:"text"})
        print(df.text.values)
        test_inputs, test_masks = self.preprocessing_for_bert(df.text.values)


        test_dataset = TensorDataset(test_inputs, test_masks)
        test_sampler = SequentialSampler(test_dataset)
        test_dataloader = DataLoader(test_dataset, sampler=test_sampler, batch_size=32)

        probs = self.bert_predict(test_dataloader)
        print(probs)

        threshold = 0.5
        preds = np.where(probs[:, 1] > threshold, 1, 1)

        return preds


    
    