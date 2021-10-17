import pandas as pd
import numpy as np

import datetime

from nltk.tokenize import sent_tokenize

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
from matplotlib import cm

from itertools import combinations

def figure1(dataframe):
    
    data = dataframe.copy()
    
    for i, r in data.iterrows():
        group = r['group']
        song = r['song']
        data.loc[i, 'x_lable'] = group+'-\n'+song
        
    ###################################################################
    
    color = ['tab:blue', 'tab:orange', 'tab:orange', 'tab:green', 'tab:green',
             'tab:purple', 'tab:purple', 'tab:brown', 'tab:pink']
    
    fig, ax = plt.subplots(figsize=(12, 8))
    data['x_lable'].value_counts().sort_index().plot.bar(color=color, zorder=3, ax=ax, width=0.8)
    
    ax.set_title('Data Distribution', size=16)
    ax.set_ylabel('count', fontsize=12)
    ax.tick_params(axis='x', labelsize=12, rotation=45)
    ax.grid(axis='y')
    
    plt.savefig('data_distribution.png', dpi=300, bbox_inches="tight")
    plt.show()
    
def figure2(dataframe):
    
    data = dataframe.copy()
    data['date'] = data['date'].astype('datetime64')
    
    ###################################################################
    
    fig, ax = plt.subplots(figsize=(12, 8))

    data['date'].value_counts().sort_index().plot(lw=2, zorder=3, ax=ax, label='_nolegend_')

    ax.plot([datetime.datetime(2015, 11, 7), datetime.datetime(2015, 11, 7)], [-15, 1500],
                    label='expedition- luv wrong\n(Nov, 2015)', lw=1)
    ax.plot([datetime.datetime(2017, 4, 11), datetime.datetime(2017, 4, 11)], [-15, 1500],
                    label='expedition- feel like this\n(Apr, 2017)', lw=1)
    ax.plot([datetime.datetime(2019, 7, 12), datetime.datetime(2019, 7, 12)], [-15, 1500],
                    label='uhsn- popsicle\n(July, 2019)', lw=1)
    ax.plot([datetime.datetime(2020, 5, 3), datetime.datetime(2020, 5, 3)], [-15, 1500],
                   label='5high- piri\n(May, 2020)', lw=1)
    ax.plot([datetime.datetime(2020, 5, 5), datetime.datetime(2020, 5, 5)], [-15, 1500],
                    label='kaachi- yourturn\n(May, 2020)', lw=1)
    ax.plot([datetime.datetime(2020, 10, 16), datetime.datetime(2020, 10, 16)], [-15, 1500],
                    label='blackswan- tonight\n(Oct, 2020)', lw=1)
    ax.plot([datetime.datetime(2020, 10, 31), datetime.datetime(2020, 10, 31)], [-15, 1500],
                    label='prisma- breakou\n(Oct, 2020)', lw=1)
    ax.plot([datetime.datetime(2020, 11, 5), datetime.datetime(2020, 11, 5)], [-15, 1500],
                    label='kaachi- photo magic\n(Nov, 2020)', lw=1)
    ax.plot([datetime.datetime(2021, 10, 14), datetime.datetime(2021, 10, 14)], [-15, 1500],
                    label='blackswan- close to me\n(Nov, 2020)', lw=1)

    ax.set_title('Data Time Distribution', size=16)
    
    fmt_half_year = mdates.MonthLocator(interval=6)
    ax.xaxis.set_major_locator(fmt_half_year)

    fmt_month = mdates.MonthLocator()
    ax.xaxis.set_minor_locator(fmt_month)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    
    ax.set_xlim([datetime.datetime(2015, 10, 1), datetime.datetime(2021, 12, 1)])

    ax.set_ylabel('count', fontsize=12)
    ax.set_ylim([-10, 1200])

    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    ax.grid(axis='y')
    ax.legend(loc=(1.01, 0), title='debut date', fontsize=12, title_fontsize=12)

    plt.savefig('data_time_distribution.png', dpi=300, bbox_inches="tight")
    plt.show()
    
def figure3(dataframe):
    
    df = pd.DataFrame(columns=['group'])

    for g in dataframe['group'].unique():
        df.at[df.shape[0], 'group'] = g

    df = df.set_index('group')

    for g in dataframe['group'].unique():    
        result = dataframe.groupby('group')['language'].value_counts(normalize=True).loc[g][:3]

        for i in result.index:
            num = round(result[i], 3)
            df.at[g, i] = num

    for i, r in df.iterrows():
        acc = r[:].sum()
        df.at[i, 'others'] = 1-acc

    df = df.apply(lambda x: x*100)
    df.columns = ['English', 'Spanish', 'Korean', 'portuguese', 'German', 'Somali', 'Arabic',
                   'Indonesian', 'Tagalog', 'others']

    df = df.sort_values(by=['English'])
    df = df.fillna(0)

    ###################################################################
    
    groups = list(df.index)

    languages = list(df.columns)
    data = np.array(df)
    data_cum = data.cumsum(axis=1)
    language_colors  = cm.get_cmap('tab10').colors

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.set_title('What Language Do Commenters of Multinational K-Pop Use?', fontsize=16)

    ax.set_xlim([0, 100])
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())

    ax.invert_yaxis()

    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    for i, (lang, color) in enumerate(zip(languages, language_colors)):

        widths = data[:, i]
        starts = data_cum[:, i] - widths
        ax.barh(groups, widths, left=starts, height=0.8, label=lang, color=color, zorder = 2)

    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False) 

    ax.grid('x')
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 0.6), fontsize=12)

    plt.savefig('language_use.png', dpi=300, bbox_inches="tight")
    plt.show()
    
def figure4(dataframe):
    
    labels = ['quality', 'nationalist_ethnicist', 'kpop']

    q = dataframe['quality'].value_counts()[1]
    e = dataframe['nationalist_ethnicist'].value_counts()[1]
    k = dataframe['kpop'].value_counts()[1]

    x = np.arange(len(labels))
    y = [q, e, k]

    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.bar(x, y, zorder=2)

    ax.set_title('Classification Count', fontsize=16)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)

    ax.set_ylabel('count', fontsize=12)
    ax.set_ylim([0, 1100])
    ax.tick_params(axis='y', labelsize=12)

    ax.bar_label(bars, fontsize=14)
    ax.grid(axis='y', zorder=0)

    for k, spine in ax.spines.items():  #ax.spines is a dictionary
        spine.set_zorder(10)

    plt.savefig('classification_count.png', dpi=300)
    plt.show()
    
def figure5(dataframe):
    
    pd.options.display.max_colwidth = 300
    
    q = dataframe.loc[dataframe['quality']==1, 'text'].sample(3)
    ne = dataframe.loc[dataframe['nationalist_ethnicist']==1, 'text'].sample(3)
    k = dataframe.loc[dataframe['kpop']==1, 'text'].sample(3)
    
    snippet = pd.DataFrame(zip(q, ne, k), columns=['quality', 'nationalist_ethnicist', 'kpop'])
    
    return snippet


'''
    The following four functions were made to evaluate tfidf model.
'''

def top_tfidf_feats(row, features, top_n=25):
    
    # Get top n tfidf values in row and return them with their corresponding feature names.

    topn_ids = np.argsort(row)[::-1][:top_n]
    top_feats = [(features[i], row[i]) for i in topn_ids]
    
    df = pd.DataFrame(top_feats)
    df.columns = ['feature', 'tfidf']
    
    return df

def top_feats_in_doc(Xtr, features, row_id, top_n=25):
    
    # Top tfidf features in specific document (matrix row)
    
    row = np.squeeze(Xtr[row_id].toarray())
    return top_tfidf_feats(row, features, top_n)

def top_mean_feats(Xtr, features, grp_ids=None, min_tfidf=0.1, top_n=25):
    
    # Return the top n features that on average are most important amongst documents in rows
    #    indentified by indices in grp_ids.
    
    if grp_ids:
        D = Xtr[grp_ids].toarray()
    else:
        D = Xtr.toarray()

    D[D < min_tfidf] = 0
    tfidf_means = np.mean(D, axis=0)
    return top_tfidf_feats(tfidf_means, features, top_n)

def top_feats_by_class(Xtr, y, features, min_tfidf=0.1, top_n=25):
    
    # Return a list of dfs, where each df holds top_n features and their mean tfidf value
    #   calculated across documents with the same class label.
    
    dfs = []
    labels = np.unique(y)
    
    for label in labels:
        
        ids = np.where(y==label)
        feats_df = top_mean_feats(Xtr, features, ids, min_tfidf=min_tfidf, top_n=top_n)
        feats_df.label = label
        dfs.append(feats_df)
        
    df0, df1 = tuple(dfs)
    
    return df0, df1


def visualize_tfidf_model(vectorizer, data_tfidf, dataframe, cat_col):
    
    features = vectorizer.get_feature_names()
    _0, _1 = top_feats_by_class(data_tfidf, dataframe[cat_col].values, features, min_tfidf=0.1, top_n=25)
    
    y_1 = _1['feature']
    x_1 = _1['tfidf']

    y_0 = _0['feature']
    x_0 = _0['tfidf']

    fig, axs = plt.subplots(1, 2, figsize=(12, 9))
    axs[0].barh(y_1, x_1)
    axs[1].barh(y_0, x_0)

    axs[0].set_title('Comments about '+str(cat_col))
    axs[0].set_xlabel('mean tf-idf score')
    axs[0].spines['right'].set_visible(False)
    axs[0].spines['top'].set_visible(False)
    axs[0].set_ylim([-1, 25])
    axs[0].invert_yaxis()

    axs[1].set_title('Comments not about '+str(cat_col))
    axs[1].set_xlabel('mean tf-idf score')
    axs[1].spines['right'].set_visible(False)
    axs[1].spines['top'].set_visible(False)
    axs[1].set_ylim([-1, 25])
    axs[1].invert_yaxis()
    
    plt.savefig('tfidf_model_'+str(cat_col)+'.png', dpi=300)
    plt.show()
    
def figure6(dataframe):

    doc = list()

    for text in dataframe['processed_text']:
        sentences = sent_tokenize(text)
        for s in sentences:
            doc.append(s)
    
    #add a space after black to avoid sampling instance of blackswan
    concept_list = [('music', 'song'), ('voice', 'vocal'), ('dance', 'choreography'), ('language', 'pronunciation'),
                ('asian',), ('indian',), ('white',), ('black ',), ('race',), ('kpop',), ('training',), ('company',)]

    node_list = ['song', 'voice', 'dance', 'language', 'asian', 'indian', 'white', 'black', 'race',
                 'kpop', 'training', 'culture']

    cc = combinations(concept_list, 2)
    dd = list()

    for o, t in cc:
        dd.append([o, t, np.nan])

    for node in dd:
        node[2] = 0

        for sentence in doc:
            if (any(word in sentence for word in node[0])) & (any(word in sentence for word in node[1])):
                node[2] += 1

    node_dict = dict()
    for c, n in zip(concept_list, node_list):
        node_dict[c] = n

    for i in dd:
        i[0] = node_dict[i[0]]
        i[1] = node_dict[i[1]]

    ###########################################################################
    
    fig, ax = plt.subplots(figsize=(8, 8))

    G = nx.Graph()

    node_list = node_list
    for node in node_list:
        G.add_node(node)

    group_attr_dict = {'song': 'quality', 'voice': 'quality', 'dance': 'quality', 'language': 'quality',
                       'asian': 'nationalist_ethnicist', 'indian': 'nationalist_ethnicist',
                       'white': 'nationalist_ethnicist', 'black': 'nationalist_ethnicist',
                       'race': 'nationalist_ethnicist',
                       'kpop': 'kpop', 'training': 'kpop', 'culture': 'kpop'}

    nx.set_node_attributes(G, group_attr_dict, name='group')

    node_color = list()

    for node in G.nodes(data=True):

        if 'quality' in node[1]['group']:
            node_color.append('palegreen')

        elif 'nationalist_ethnicist' in node[1]['group']:
            node_color.append('sandybrown')

        elif 'kpop' in node[1]['group']:
            node_color.append('skyblue')

    pos=nx.circular_layout(G) 
    nx.draw_networkx_nodes(G,pos,node_color=node_color,node_size=1000)

    labels = {}
    for node_name in node_list:
        labels[str(node_name)] =str(node_name)

    nx.draw_networkx_labels(G,pos,labels,font_size=12)

    for i in range(len(dd)):

        interaction = dd[i]
        a = interaction[0]
        b = interaction[1]
        w = interaction[2]
        G.add_edge(a, b, weight=w)

    all_weights = []

    for (node1,node2,data) in G.edges(data=True):
        all_weights.append(data['weight'])

    unique_weights = list(set(all_weights))

    for weight in unique_weights:

        weighted_edges = [(node1,node2) for (node1,node2,edge_attr) in G.edges(data=True) if edge_attr['weight']==weight]
        width = (weight/max(unique_weights))*10
        nx.draw_networkx_edges(G,pos,edgelist=weighted_edges,width=width)

    for c, l in zip(['palegreen', 'sandybrown', 'skyblue'], ['quality', 'nationalist_ethnicist', 'kpop']):
        plt.scatter([],[], s=100, c=c, label=l)

    ax.set_title('Network of Concepts', fontsize=16)

    al = ax.legend(loc=(0.95, 0), title='Classification', fontsize=12, title_fontsize=14)
    ax.add_artist(al)
    ax.axis('off')

    ax2 = ax.twinx()
    for weight in [50, 100, 150]:
        ax2.plot([], [], c='black', lw=(weight/max(unique_weights))*10, label=str(weight))
    ax2.get_yaxis().set_visible(False)

    ax2.legend(loc=(0.95, 0.8), title='Count', borderpad=0.6,
               fontsize=12, title_fontsize=14)
    ax2.axis('off')

    plt.savefig('network_of_concepts.png', dpi=300, bbox_inches="tight")
    plt.show()
    
def figure7(about, dataframe, sentiment_data):
    
    # 
    # about = 'Quality' or 'Nationalist and Ethnicist'
    #
    # sentiment_data == {aspect1: [(sentiment, group), (sentiment, group)...],
    #                    asepct2: ...}
    #
    
    group_dic = dict()
    
    for who in list(dataframe['group'].unique()):
        group_dic[who] = list()
    
    for aspect, lst in sentiment_data.items():
        for ps, who in lst:
            group_dic[who].append(ps)
            
    for who, lst in group_dic.items():
        
        size = len(lst)
        neg = lst.count('neg')
        neu = lst.count('neu')
        pos = lst.count('pos')
        
        temp = [neg/size, neu/size, pos/size]
        temp = [100*round(i, 3) for i in temp]
        group_dic[who] = temp
        
    group_dic = dict(sorted(group_dic.items(), key=lambda item: item[1][0]))
        
    ############################################################
    
    category_names = ['negative', 'neutral', 'positive']
    
    labels = list(group_dic.keys())
    
    data = np.array(list(group_dic.values()))
    data_cum = data.cumsum(axis=1)
    
    category_colors = plt.get_cmap('RdYlGn')(
        np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(12, 8))
    #ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())
    ax.tick_params(axis='y', labelsize=12)

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=0.75,
                        label=colname, color=color)

        r, g, b, _ = color
        text_color = 'snow' if r * g * b < 0.5 else 'black'
        ax.bar_label(rects, label_type='center', color=text_color, fmt='%.1f%%', fontsize=12)
    
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
     
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, -0.1),
              loc='lower left', fontsize=12)
    
    ax.set_title('Sentiment Distribution of Comments about '+about, fontsize=16)
    
    for k, spine in ax.spines.items():  #ax.spines is a dictionary
        spine.set_zorder(10)
    
    plt.savefig('sentiment_distribution_'+about+'.png', dpi=300)
    plt.show()
    
def figure8(dataframe, sentiment_data):
    
    #
    # sentiment_data == {aspect1: [(sentiment, group), (sentiment, group)...],
    #                    asepct2: ...}
    #
    
    group_dic = dict()
    aspect_list = list()
    
    for who in list(dataframe['group'].unique()):
        
        group_dic[who] =  dict()
        group_dic[who]['count'] = list()
        group_dic[who]['perc'] = list()
    
    for aspect, lst in sentiment_data.items():
        aspect_list.append(aspect)
        
        for ps, who in lst:
            
            if ps == 'neg':
                
                group_dic[who]['count'].append(aspect)
                group_dic[who]['perc'].append(aspect)
                
    for g, dic in group_dic.items():
        
        count_dic = dict()
        
        for aspect in aspect_list:
            
            ac = dic['count'].count(aspect)
            count_dic[aspect] = ac
            
        group_dic[g]['count'] = count_dic
        
        perc_dic = dict()
        size = len(dic['perc'])
        
        for aspect in aspect_list:
        
            ac = dic['perc'].count(aspect)
            perc_dic[aspect] = ac/size
            
        group_dic[g]['perc'] = perc_dic
        
    ##################################################################
    
    points = list()
    counts = list()
    
    for g, d in group_dic.items():
        for k, v in d['count'].items():
            counts.append(v)
    m = max(counts)

    for group, d in group_dic.items():

        for aspect in d['perc']:

            perc = d['perc'][aspect]
            count = d['count'][aspect]
            weight = count/m

            point = (perc, group, aspect, weight)
            points.append(point)
    
    ###################################################################

    def aspect_to_c(x):

        dic = dict()
        for a, c in zip(aspect_list, ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']):
            dic[a] = c
        return(dic[x])

    x = [a*100 for (a, b, c, d) in points]
    y = [b for (a, b, c, d) in points]
    aspect = [aspect_to_c(c) for (a, b, c, d) in points]
    size = [d*5000 for (a, b, c, d) in points]

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.scatter(x, y, c=aspect, s=size, alpha=0.6)

    ax.set_title('Percentages of Negative Sentiments about Different Aspects of Quality', fontsize=16)

    ax.set_xlim([-5, 100])
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())

    ax.set_ylim([-1, 6])

    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    ax.grid(True)

    for a in aspect_list:
        ax.scatter([],[], s=120, c=aspect_to_c(a), label=a)

    al = ax.legend(loc=(1.03, 0), fontsize=12, frameon=False, labelspacing=1,
                   title='Aspects', title_fontsize=14)
    ax.add_artist(al)

    ax2 = ax.twinx()
    for count in [10, 30, 50]:
        ax2.scatter([], [], c='tab:grey', alpha=0.6, s=count/m*5000, label=str(count))
    ax2.get_yaxis().set_visible(False)

    ax2.legend(loc=(1.07, 0.5), labelspacing=3, frameon=False, title='Count',
               fontsize=10, title_fontsize=14)

    plt.savefig('negative_quality.png', dpi=300, bbox_inches="tight")
    plt.show()
    
def figure9(sentiment_data):

    #
    # sentiment_data == {aspect1: [(sentiment, group), (sentiment, group)...],
    #                    asepct2: ...}
    #
    
    # (perc, aspect, sent_type, count)
    
    results = dict()    
    aspect_dic = dict()
    
    for aspect in sentiment_data:
        
        results[aspect] = dict()
        aspect_dic[aspect] = list()

    for aspect, lst in sentiment_data.items():
        
        for ps, who in lst:
            aspect_dic[aspect].append(ps)
            
    #aspect_dic = {aspect: [neg, neg, neu, ...]}
                
    for a, lst in aspect_dic.items():
        
        neg_ = list()
        neu_ = list()
        pos_ = list()
            
        size = len(lst)
        
        for ps in lst:
            if ps == 'neg':
                neg_.append(ps)
            if ps == 'neu':
                neu_.append(ps)
            if ps == 'pos':
                pos_.append(ps)
        
        results[a]['neg'] = [len(neg_)/size, len(neg_)]
        results[a]['neu'] = [len(neu_)/size, len(neu_)]
        results[a]['pos'] = [len(pos_)/size, len(pos_)]
        
    #############################################################
        
    points_dic = results
        
    points = list()

    counts = list()
    percs = list()
    sents = list()
    aspects = list()

    for a, dic1 in points_dic.items():
        for s, dic2 in dic1.items():

            percs.append(round(dic2[0], 3))
            aspects.append(a)
            sents.append(s)
            counts.append(dic2[1])

    m = max(counts)

    weights = [i/m for i in counts]

    for p, a, s, w in zip(percs, aspects, sents, weights):
        points.append((p, a, s, w))

    # poinst = [(perc, aspect, sent_type, count)]
    
    ##############################################################
    
    sent_list = ['negative', 'neutral', 'postive']

    def s_to_l(x):

        dic = dict()
        for s, l in zip(['neg', 'neu', 'pos'], sent_list):
            dic[s] = l
        return dic[x]

    def sent_to_c(x):

        dic = dict()
        for a, c in zip(sent_list, ['tab:red', 'tab:olive', 'tab:green']):
            dic[a] = c
        return dic[x]

    x = [a*100 for (a, b, c, d) in points]
    y = [b for (a, b, c, d) in points]
    sent = [sent_to_c(s_to_l(c)) for (a, b, c, d) in points]
    size = [d*5000 for (a, b, c, d) in points]

    fig, ax = plt.subplots(figsize=(12, 8))

    ax.scatter(x, y, c=sent, s=size, alpha=0.6)

    ax.set_title('Percentages of Different Sentiments with Nationalist-Ethnicist Utterance', fontsize=16)

    ax.set_xlim([0, 75])
    ax.set_xticks([10, 20, 30, 40, 50, 60, 70])
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())

    ax.set_ylim([-1, 5])

    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    ax.grid(True)

    for a in sent_list:
        ax.scatter([],[], s=120, c=sent_to_c(a), label=a)

    al = ax.legend(loc=(1.03, 0), fontsize=12, frameon=False, labelspacing=1,
                   title='Sentiment', title_fontsize=14)
    ax.add_artist(al)

    ax2 = ax.twinx()
    for count in [50, 100, 150]:
        ax2.scatter([], [], c='tab:grey', alpha=0.6, s=count/m*5000, label=str(count))
    ax2.get_yaxis().set_visible(False)

    ax2.legend(loc=(1.07, 0.5), labelspacing=3, frameon=False, title='Count',
               fontsize=10, title_fontsize=14)

    plt.savefig('nationalist_ethnicist_sentiment_distribution_by_aspect', dpi=300, bbox_inches="tight")
    plt.show()