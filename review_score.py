# coding=utf-8
import numpy as np
import pandas as pd
import math
import nltk
d = pd.DataFrame()
cities = ["nyc", "boston", "portland", "sf", "la", "seattle", "chicago", "dc", 
          "montreal", "toronto" ,"sydney", "london", "melbourne"]
# cities = ["nyc", "boston"]

for c in cities:
    tmp_d = pd.read_csv('listings_' + c + '.csv',sep=',',dtype=pd.np.str)
    tmp_d['listing_city'] = c
    d = d.append(tmp_d, ignore_index=True)

desc_sent = []
for s in d["description"]:
    s=str(s).strip().decode("ascii","ignore").encode("ascii")
    desc_sent.append(nltk.sent_tokenize(s))

self_reference_dict = ["I", "me", "my", "we", "us", "our", "mine", "myself", "ourselves", "ours"]
self_reference_score = []

for sents in desc_sent:
    cnt = 0
    flg = False
    if (len(sents) == 0): 
        self_reference_score.append(0)
        continue
    for s in sents:
        words = nltk.word_tokenize(s)
        for w in self_reference_dict:
            if w in words:
                cnt += 1
                flg = True
                break
        if (flg):
#             print s
            flg = False
    self_reference_score.append(cnt/float(len(sents)))

d = d.join(pd.DataFrame({'self_reference_score': self_reference_score}))

tot_self_reference_score = pd.DataFrame(data=np.zeros((10, len(cities))), columns=cities)
cnt = pd.DataFrame(data=np.zeros((10, len(cities))), columns=cities)
ave_self_reference_score = pd.DataFrame(data=np.zeros((10, len(cities))), columns=cities)

for i,score in enumerate(d['review_scores_value']):
    if math.isnan(float(score)) == False:
        tot_self_reference_score[d['listing_city'][i]][int(score) - 1] += d['self_reference_score'][i]
        cnt[d['listing_city'][i]][int(score) - 1] += 1

print "\n"
print "review_scores_value\taverage_self_reference_score"
for c in cities:
    print c
    for i in range(10):
        ave_self_reference_score[c][i] = 0
        if float(cnt[c][i]) > 0:
            ave_self_reference_score[c][i] = float(tot_self_reference_score[c][i])/int(cnt[c][i])
            print i+1, "\t\t\t", ave_self_reference_score[c][i]

from math import pi

from bokeh.models import HoverTool
from bokeh.plotting import ColumnDataSource, figure, show, output_file
scores = [1,2,3,4,5,6,7,8,9,10]

colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce",
          "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]

city = []
score = []
color = []
rate = []
for c in cities:
    for s in scores:
        city.append(c)
        score.append(str(s))
        rate.append(ave_self_reference_score[c][s-1])
        color.append(colors[min(max(int(ave_self_reference_score[c][s-1]*50), 0), 8)])

source = ColumnDataSource(
    data=dict(city=city, score=score, color=color, rate=rate)
)

TOOLS = "resize,hover,save,pan,box_zoom,wheel_zoom"

p = figure(title="Self-reference word : Review score",
           x_range=map(str, scores), y_range=list(reversed(cities)),
           x_axis_location="below", plot_width=500, plot_height=500,
           toolbar_location="left", tools=TOOLS)

p.grid.grid_line_color = None
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.axis.major_label_text_font_size = "10pt"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = pi/3

p.rect("score", "city", width=1, height=1, source=source,
       color="color", line_color=None)

p.select_one(HoverTool).tooltips = [
    ('city', '@city'),
    ('self-reference-rate', '@rate'),
]

output_file('review_score.html', title="Self-reference word : Review score")

show(p)      # show the plot
