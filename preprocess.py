import os
import re
import jieba
import pandas as pd
import numpy as np
import file_location

keywords_list = ['中国', '翻墙', '河蟹', '被河蟹', '五毛党', '五毛', '谷歌', '被和谐', '民主', '文革', '文化大革命', '茉莉花革命', '茉莉花', '示威', '抗议', '集会', '民众', '新闻自由', '言论自由', '宗教自由', '信仰自由', '台独', '藏独', '港独', '疆独', '新疆', '雾霾', '达赖喇嘛', '三聚氰胺', '地沟油', '毒奶粉', '雾霾', '豆腐渣', '薄熙来', 'bxl', '艾未未', '刘晓波', '晓波', 'lxb', '天安门', '六四', '知识产权', '山寨', '盗版', '三峡', '贫富', '洗脑', '人权', '维稳', '维权', '移民', '移居', '外资', '南海争议', '钓鱼岛', '钓鱼台', '女权', '爱国', '爱党', '奥巴马', '欧巴马', '共产党', '计划生育', '一孩政策', '红黄蓝', '三色幼儿园', '川普', '特朗普', '政改', '温家宝', '胡锦涛', 'wjb', 'hjt']

def add_topic_and_class_column(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + file_name)
            if f.endswith(b'_censored.csv') and f.startswith(b'jed'):          
                topic = file_name[4:-13]
                df['topic'] = topic
                df['class'] = 'censored'

            elif f.endswith(b'_uncensored.csv') and f.startswith(b'jed'):
                topic = file_name[4:-15]
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

    censored_merged_df.to_csv(directory + '/' + file_name[:3] + '_all_censored.csv', index=False)
    uncensored_merged_df.to_csv(directory + '/' + file_name[:3] + '_all_uncensored.csv', index=False)

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
            df = pd.read_csv(directory + '/' + file_name)

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
            df = pd.read_csv(directory + '/' + file_name)
            print('before {}'.format(df.shape))
            for index, data in df.iterrows():
                if type(data['content']) is not str or len(data['content']) <= 5 or '好声音' in data['content'] or '中国移动' in data['content'] or '音乐' in data['content'] or '一善' in data['content']:
                    df.drop(index, inplace=True)
            print('after {}'.format(df.shape))
            df.to_csv(directory + '/' + file_name, index=False)


def sort_by_content(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + file_name)
            df.sort_values(by=['content']).to_csv(directory + '/' + file_name, index=False)


def remove_similar(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + file_name)

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


def remove_irrelevant(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            relevant = []
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + file_name)
            df_drop = pd.read_csv(directory + '/' + file_name)
            print(df.shape)
            
            for index, data in df.iterrows():
                if data['topic'] != 'everythingElse':
                    if not any(keyword in data['content'] for keyword in keywords_list):
                        df_drop.drop(index, inplace=True)
            print(df_drop.shape)


def segment(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + f.decode('utf-8'))
            print(df.shape)

            for word in keywords_list:
                jieba.add_word(word)
                jieba.suggest_freq(word, True)

            segmented_data = []
            for index, data in df.iterrows():
                data['content'] = jieba.cut(data['content'], cut_all=False, HMM=True)
                data['content'] = ' '.join(data['content'])
                data['content'] = re.sub(r'\s+', ' ', data['content'])
                segmented_data.append(data)

            print(pd.DataFrame(segmented_data).shape)

            pd.DataFrame(segmented_data).to_csv(directory + '/' + file_name, index=False)

def convert_punctuations(directory):

    comma = re.compile(r'，')
    period = re.compile(r'。')
    comma_chi = re.compile(r'、')
    semi_colon = re.compile(r'；')
    colon = re.compile(r'：')
    open_quote = re.compile(r'「')
    close_quote = re.compile(r'」')
    open_quote_2 = re.compile(r'『')
    close_quote_2 = re.compile(r'』')
    open_paren = re.compile(r'（')
    close_paren = re.compile(r'）')
    open_bracket = re.compile(r'【')
    close_bracket = re.compile(r'】')
    question_mark = re.compile(r'？')
    exclamation_mark = re.compile(r'！')
    dash = re.compile(r'──')
    elipses = re.compile(r'……')
    elipses_2 = re.compile(r'⋯')
    dash_short = re.compile(r'—')
    pound = re.compile(r'＃')
    dollar = re.compile(r'＄')
    percent = re.compile(r'％')
    ampersand = re.compile(r'＆')
    asterisk = re.compile(r'＊')
    plus = re.compile(r'＋')
    forward_slash = re.compile(r'／')
    less_than = re.compile(r'＜')
    more_than = re.compile(r'＞')
    equal = re.compile(r'＝')
    trail = re.compile(r'～')

    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + f.decode('utf-8'))
            converted = []

            for index, data in df.iterrows():
                data['content'] = re.sub(comma, ',', data['content'])
                data['content'] = re.sub(period, '.', data['content'])
                data['content'] = re.sub(comma_chi, ',', data['content'])
                data['content'] = re.sub(semi_colon, ';', data['content'])
                data['content'] = re.sub(colon, ':', data['content'])
                data['content'] = re.sub(open_quote, '"', data['content'])
                data['content'] = re.sub(close_quote, '"', data['content'])
                data['content'] = re.sub(open_quote_2, '"', data['content'])
                data['content'] = re.sub(close_quote_2, '"', data['content'])
                data['content'] = re.sub(open_paren, '(', data['content'])
                data['content'] = re.sub(close_paren, ')', data['content'])
                data['content'] = re.sub(open_bracket, '[', data['content'])
                data['content'] = re.sub(close_bracket, ']', data['content'])
                data['content'] = re.sub(question_mark, '?', data['content'])
                data['content'] = re.sub(exclamation_mark, '!', data['content'])
                data['content'] = re.sub(dash, '_', data['content'])
                data['content'] = re.sub(elipses, '…', data['content'])
                data['content'] = re.sub(elipses_2, '…', data['content'])
                data['content'] = re.sub(dash_short, '-', data['content'])
                data['content'] = re.sub(pound, '#', data['content'])
                data['content'] = re.sub(dollar, '$', data['content'])
                data['content'] = re.sub(percent, '%', data['content'])
                data['content'] = re.sub(ampersand, '&', data['content'])
                data['content'] = re.sub(asterisk, '*', data['content'])
                data['content'] = re.sub(plus, '+', data['content'])
                data['content'] = re.sub(forward_slash, '/', data['content'])
                data['content'] = re.sub(less_than, '<', data['content'])
                data['content'] = re.sub(more_than, '>', data['content'])
                data['content'] = re.sub(equal, '=', data['content'])
                data['content'] = re.sub(trail, '~', data['content'])
                data['content'] = data['content'].lstrip()
                data['content'] = data['content'].rstrip()

                converted.append(data)

            print(pd.DataFrame(converted).shape)
            pd.DataFrame(converted).to_csv(directory + '/punc_' + file_name, index=False)

# convert_punctuations(file_location.jed_data)

def rename_and_drop_columns(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + f.decode('utf-8'))

            if 'uncensored' in file_name:
                df.rename(columns={'A': 'idx', 'B': 'content', 'L': 'followers', 'N': 'topic', 'O': 'class'}, inplace=True)
                df.drop(columns=['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'M'], inplace=True)
            else:
                df.rename(columns={'Source (A)': 'idx', 'Source (B)': 'content', 'Source (L)': 'followers', 'Source (N)': 'topic', 'Source (O)': 'class'}, inplace=True)
                df.drop(columns=['Source (C)', 'Source (D)', 'Source (E)', 'Source (F)', 'Source (G)', 'Source (H)', 'Source (I)', 'Source (J)', 'Source (K)', 'Source (M)'], inplace=True)

            df.to_csv(directory + '/' + file_name, index=False)


def extract_content_to_txt(directory):
    for f in os.listdir(os.fsencode(directory)):
        if f.endswith(b'.csv'):
            file_name = f.decode('utf-8')
            df = pd.read_csv(directory + '/' + f.decode('utf-8'))
            np.savetxt(directory + '/' + file_name.replace('csv', 'txt'), df['content'], fmt='%s' , newline='\n')
