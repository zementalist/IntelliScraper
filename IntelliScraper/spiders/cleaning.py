# import re
# from bs4 import BeautifulSoup
# import pandas as pd

# # may be changed or removed


# def cleaning(df):
#     current_country = ''
#     current_company_name = ''
#     current_country_wikilink = ''
#     index_flag = False
#     temp_dict = {"country": '', "company": '', "wikipedia_link": ''}
#     full_list = []
#     for v in range(4):
#         mix_str = df.iloc[v][0]
#         doc = BeautifulSoup(mix_str, 'html.parser')
#         tags = doc.find_all(['h2', 'td'])

#         for i in range(len(tags)):
#             if str(tags[i])[:3] == "<h2":
#                 current_country = str(tags[i].span.string)
                
#             elif str(tags[i])[:3] == "<td":
#                 if index_flag == False and len(str(tags[i])) < 40 and len(str(tags[i])) > 16:
#                     index_flag = True
#                 elif index_flag == True:
#                     match = re.search(r'(?<=">)(.*)(?=<\/a>)', str(tags[i]))
#                     if match:
#                         current_company_name = match.group(1)
#                         match2 = re.search(r'(?=<|\()(.*)', current_company_name)
#                         if match2:
#                             # print(match2.group(1), '-----')
#                             current_company_name = re.sub('(?=<|\()(.*)', '', match2.group(1)).strip()
#                             # print(current_company_name)
                            
                        
#                     match = re.search(r'index\.php', str(tags[i]))
#                     if match:
#                         current_country_wikilink = 'null'
#                     else:
#                         current_country_wikilink = ''.join(["http://en.wikipedia.org" ,tags[i].a['href'] if tags[i].a else "null"])
#                     index_flag = False

#                     temp_dict["country"] = current_country
#                     temp_dict["company"] = current_company_name
#                     temp_dict["wikipedia_link"] = current_country_wikilink
#                     full_list.append(temp_dict)
#                     temp_dict = {"country": '', "company": '', "wikipedia_link": ''}
                    
#     new_df = pd.DataFrame(full_list)
#     return new_df
#     # new_df = new_df[new_df.wikipedia_link != 'null']
#     # return new_df[new_df.company != '']

# new_df = pd.read_csv('newdata.csv')
# result_df = cleaning(new_df)
# result_df.to_csv("resultv2.csv", index=False)