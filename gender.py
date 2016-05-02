
# coding: utf-8

# In[71]:


import numpy as np
import pandas as pd
import math
import nltk
from genderizer.genderizer import Genderizer


# In[72]:

# print Genderizer.detect(firstName = 'cell', text='insert help')


# In[73]:

d = pd.DataFrame()
cities = ["nyc", "boston", "chicago", "dc", "sf", "la", "seattle", "portland", 
          "montreal", "toronto" ,"sydney", "melbourne", "london"]
# cities = ["nyc", "london"]
for c in cities:
    tmp_d = pd.read_csv('listings_' + c + '.csv',sep=',',dtype=pd.np.str)
    tmp_d['listing_city'] = c
    d = d.append(tmp_d, ignore_index=True)


# In[74]:

desc_sent = []
for s in d["description"]:
    s=str(s).strip().decode("ascii","ignore").encode("ascii")
    desc_sent.append(nltk.sent_tokenize(s))


# In[75]:

self_reference_dict = ["I", "me", "my", "we", "us", "our", "mine", "myself", "ourselves", "ours"]


# In[76]:

self_reference_score = []
for sents in desc_sent:
    cnt = 0
    if (len(sents) == 0): 
        self_reference_score.append(0)
        continue
    for s in sents:
        words = nltk.word_tokenize(s)
        for w in self_reference_dict:
            if w in words:
                cnt += 1
                break
    self_reference_score.append(cnt/float(len(sents)))


# In[77]:

gender = []
for i, name in enumerate(d['host_name']):
    try:
#         print nltk.word_tokenize(name)[0]
        gender.append(Genderizer.detect(firstName = nltk.word_tokenize(name)[0], text=str(d['summary'][i])))
    except TypeError:
        gender.append('None')
    except ZeroDivisionError:
        gender.append(Genderizer.detect(firstName = nltk.word_tokenize(name)[0]))


# In[78]:

d = d.join(pd.DataFrame({'self_reference_score': self_reference_score}))
d = d.join(pd.DataFrame({'gender': gender}))


# In[79]:

def gender_to_int(g):
    if (g == 'male'):
        return 0
    elif (g == 'female'):
        return 1
    else:
        return 2

def int_to_gender(i):
    if (i == 0):
        return 'male'
    elif (i == 1):
        return 'female'
    else: 
        return 'None'

tot_self_reference_score = pd.DataFrame(data=np.zeros((3, len(cities))), columns=cities)
cnt = pd.DataFrame(data=np.zeros((3, len(cities))), columns=cities)
ave_self_reference_score = pd.DataFrame(data=np.zeros((3, len(cities))), columns=cities)

for i,g in enumerate(d['gender']):
    tot_self_reference_score[d['listing_city'][i]][gender_to_int(g)] += d['self_reference_score'][i]
    cnt[d['listing_city'][i]][gender_to_int(g)] += 1

print "gender\taverage_self_reference_score"
for c in cities:
    print c
    for i in range(3):
        ave_self_reference_score[c][i] = 0
        if float(cnt[c][i]) > 0:
            ave_self_reference_score[c][i] = float(tot_self_reference_score[c][i])/int(cnt[c][i])
            print int_to_gender(i), "\t", ave_self_reference_score[c][i]


# In[80]:

from math import pi

from bokeh.models import HoverTool
from bokeh.plotting import ColumnDataSource, figure, show, output_file
from bokeh.io import output_notebook


# In[88]:

scores = range(1,4)

colors = ["#D3EAC9", "#9CD5CD", "#76C7D1", "#3EA7CD", "#3583B8",
          "#2B60A3", "#213D8E", "#182075", "#131651"]

city = []
score = []
color = []
rate = []
for c in cities:
    for s in scores:
        city.append(c)
        score.append(s)
        rate.append(ave_self_reference_score[c][s-1])
        color.append(colors[min(max(int((ave_self_reference_score[c][s-1]-0.1)*300), 0), 8)])

source = ColumnDataSource(
    data=dict(city=city, score=score, color=color, rate=rate)
)

TOOLS = "hover"

p = figure(title="Self-reference word : Gender",
           x_range=map(int_to_gender, range(0,3)), y_range=list(reversed(cities)),
           x_axis_location="below", plot_width=500, plot_height=500,
           toolbar_location="left", tools=TOOLS)

p.grid.grid_line_color = None
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.axis.major_label_text_font_size = "10pt"
p.axis.major_label_standoff = 0
# p.xaxis.major_label_orientation = pi/3

p.rect("score", "city", width=1, height=1, source=source,
       color="color", line_color=None)

p.select_one(HoverTool).tooltips = [
    ('city', '@city'),
    ('self-reference-rate', '@rate'),
]

output_file('gender.html', title="Self-reference word : Gender")

show(p)


# In[ ]:

tot_score = tot_self_reference_score.sum(1)
tot_cnt = cnt.sum(1)
ave_score = np.nan_to_num(tot_score / tot_cnt)
print ave_score

from bokeh.charts import Bar
q = Bar(ave_score, title="Self-reference word : Gender", tools=TOOLS)

output_file('gender_bar.html', title="Self-reference word : Gender")

show(q)


