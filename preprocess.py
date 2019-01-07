import os
import re
import jieba
import pandas as pd
import file_location


def add_topic_and_class_column(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + file_name)
            if f.endswith(b'_censored.csv') and f.startswith(b'scrapped'):          
                topic = file_name[9:-13]
                df['topic'] = topic
                df['class'] = 'censored'

            elif f.endswith(b'_uncensored.csv') and f.startswith(b'scrapped'):
                topic = file_name[9:-15]
                df['topic'] = topic
                df['class'] = 'uncensored' 

            df.to_csv(directory + '/' + file_name, index=False)   
            print('{}: {}'.format(file_name, df.shape))


def merge_csvs(directory):
    censored_df = []
    uncensored_df = []
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + file_name)
            if f.endswith(b'_censored.csv'):
                censored_df.append(df)
            elif f.endswith(b'_uncensored.csv'):
                uncensored_df.append(df)    

    censored_merged_df = pd.concat(censored_df, sort=False)
    uncensored_merged_df = pd.concat(uncensored_df, sort=False)

    censored_merged_df.to_csv(directory + '/' + file_name[:8] + '_all_censored.csv', index=False)
    uncensored_merged_df.to_csv(directory + '/' + file_name[:8] + '_all_uncensored.csv', index=False)

    print(censored_merged_df.shape)
    print(uncensored_merged_df.shape)


def remove_duplicates(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            if 'all' in file_name:
                df = pd.read_csv(directory + '/' + file_name)
                print('{} before: {}'.format(file_name, df.shape))
                ## look at the duplicates if necessary
                # duplicates = pd.concat(dup for _, dup in df.groupby('content') if len(dup) > 1)
                df_dropped = df.drop_duplicates(subset='content')
                print('{} after: {}'.format(file_name, df_dropped.shape))
                df_dropped.to_csv(directory + '/' + file_name, index=False)


def clean_data(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            cleaned = []
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + f.decode('utf-8'))

            for index, data in df.iterrows():
                data['content'] = re.sub(r'\n+', ' ', data['content']) ## newline
                data['content'] = re.sub(r'\r', ' ', data['content']) ## linebreak
                data['content'] = re.sub(r'收起全文d', '', data['content']) ## collapse
                data['content'] = re.sub(r'(//)', '', data['content']) ## slashes
                data['content'] = re.sub(r'(@.+?)[:：;]+', ' ', data['content']) ## tagged user reply
                data['content'] = re.sub(r'(@.+?)\s+', ' ', data['content']) ## tagged user
                data['content'] = re.sub(r'(@.+?)$', ' ', data['content']) ## end of text
                data['content'] = re.sub(r'(转发微博)', '', data['content']) ## retweet
                data['content'] = re.sub(r'(转：)', '', data['content']) ## reblog
                data['content'] = re.sub(r'#', ' ', data['content']) ## hashtag
                data['content'] = re.sub(r'(→_→)', '', data['content']) ## arrows
                data['content'] = re.sub(r'(回复)', '', data['content']) ## reply
                data['content'] = re.sub(r'(网页链接)', '', data['content']) ## link
                data['content'] = re.sub(r'\[.+?\]', '', data['content']) ## emoticon text
                data['content'] = re.sub(r'', ' ', data['content']) ## special symbol
                data['content'] = data['content'].strip()
                
                cleaned.append(data)

            df_cleaned = pd.DataFrame(cleaned)
            df_cleaned.to_csv(directory + '/' + file_name, index=False)


def remove_nan_and_short_rows(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + f.decode('utf-8'))
            print('before {}'.format(df.shape))
            for index, data in df.iterrows():
                if type(data['content']) is not str or len(data['content']) <= 5:
                    df.drop(index, inplace=True)
            print('after {}'.format(df.shape))
            df.to_csv(directory + '/' + file_name, index=False)


def sort_by_content(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + f.decode('utf-8'))
            df.sort_values(by=['content']).to_csv(directory + '/' + file_name, index=False)


def remove_similar(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + f.decode('utf-8'))

            print(file_name + str(df.shape))

            ## group data by their first character
            groups = dict()
            for index, data in df.iterrows():
                if data['content'][0] in groups.keys():
                    continue
                else:
                    current = index
                    try:
                        while data['content'][0] == df.iloc[current+1]['content'][0]:
                            if data['content'][0] not in groups.keys():
                                groups[data['content'][0]] = [data]
                            groups[data['content'][0]].append(df.iloc[current+1])
                            current += 1
                    except:
                        print('end')
            
            print('no. of groups created: {}'.format(len(groups)))

            ## remove similar posts
            similar = []
            for key, value in groups.items():
                if len(value) > 1:
                    for i in range(len(value) - 1):
                        if len(value[i]['content']) > 15:
                            cutoff = int(len(value[i]['content']) / 2)
                            if value[i]['content'][:cutoff] in value[i+1]['content'][:cutoff]:
                                # print(value[i+1]['content'])
                                similar.append(value[i+1]['mid'])
            print('similar posts found: {}'.format(len(similar)))

            for index, data in df.iterrows():
                if data['mid'] in similar:
                    df.drop(index, inplace=True)
            print(df.shape)

            df.to_csv(directory + '/' + file_name, index=False)


def segment(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + f.decode('utf-8'))
            print(df.shape)

            word_list = ['雾霾', '维稳', '维权', '洗脑', '天安门', '六四', '民运', '爱国', '爱党', '奥巴马', '欧巴马', '共产党', '薄熙来', '三聚氰胺', '地沟油', '毒奶粉', '被河蟹', '五毛党', '五毛', '谷歌', '河蟹', '被和谐', '翻墙', '计划生育', '一孩政策', '文革', '文化大革命', '红黄蓝', '三色幼儿园', '川普', '特朗普', '推特', '茉莉花革命', '新闻自由', '言论自由', '宗教自由', '信仰自由', '台独', '藏独', '港独', '疆独', '新疆', '达赖喇嘛', '艾未未', '刘晓波', '晓波', '知识产权', '山寨', '三峡', '贫富悬殊', '贫富', '外资', '南海争议', '钓鱼岛', '钓鱼台', '政改', '女权', '温家宝', '胡锦涛']

            for word in word_list:
                jieba.add_word(word)
                jieba.suggest_freq(word, True)

            segmented_data = []
            for index, data in df.iterrows():
                data['content'] = jieba.cut(data['content'], cut_all=False, HMM=True)
                data['content'] = ' '.join(data['content'])
                segmented_data.append(data)

            print(pd.DataFrame(segmented_data).shape)

            pd.DataFrame(segmented_data).to_csv(directory + '/' + file_name, index=False)