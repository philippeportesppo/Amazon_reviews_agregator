from amazon.api import AmazonAPI
import requests
import urllib
from BeautifulSoup import *
import sys
import csv
from requests.packages.urllib3.util import Retry
from requests.adapters import HTTPAdapter
from requests import exceptions
import os

try: #aws_key, aws_secret, aws_associate_tag
    API_KEY_AMAZON = os.environ['API_KEY_AMAZON'] 
    API_SECRET_AMAZON = os.environ['API_SECRET_AMAZON'] 
    API_ASSOCIATE_AMAZON = os.environ['API_ASSOCIATE_AMAZON']
except:
    print "No API_KEY_AMAZON, API_SECRET_AMAZON or API_ASSOCIATE_AMAZON found in OS environment variables"
    exit()
print "Detected API_KEY_AMAZON: ",API_KEY_AMAZON
print "Detected API_KEY_AMAZON: ",API_SECRET_AMAZON
print "Detected API_KEY_AMAZON: ",API_ASSOCIATE_AMAZON

try:
    BrowseNode=sys.argv[1]
except:
    print "No Browse Node Id provided. (example: 565108)"
    exit()

print "Detected Browse Node Id: ",BrowseNode

export_ASIN=False
try: 
    if sys.argv[2]=="export_ASIN":
        export_ASIN=True
except:
    print "No export_ASIN set: only export rating and reviews"

    
count=0
star=0
reviews=""
counter = 0   
s = requests.Session()
s.mount('https://', HTTPAdapter(max_retries=Retry(total=5, status_forcelist=[500,503,429])))

with open('Listamazon.tsv', mode='w') as fd:
    writer = csv.writer(fd, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONNUMERIC)    
    amazon = AmazonAPI(API_KEY_AMAZON, API_SECRET_AMAZON, API_ASSOCIATE_AMAZON)

    bn=amazon.browse_node_lookup(BrowseNodeId=BrowseNode)
    for s_i in bn:
        print "Found ",len(s_i.children)," Node Ids under ",BrowseNode
        
        for index_i in range(0,len(s_i.children)):
            print "Parsing Node Id: ",s_i.children[index_i].id
        
            products=amazon.search(BrowseNode=s_i.children[index_i].id, SearchIndex='Electronics')
                
            for i,product_val in enumerate(products):
                
                print "Parsing ASIN: ",product_val.asin
                product = amazon.lookup(ItemId=product_val.asin)
                       
                try:    
                    r=s.get(url=product.reviews[1])
                    
                    soup = BeautifulSoup(r.text)
                    
                    tags = soup('a')

                    extract_href = re.findall('<a href="(\S+)"', str(tags[len(tags)-1]))
                    
                    try:
                        
                        r=s.get(url=extract_href[0]+"/ref=cm_cr_getr_d_paging_btm_1?ie=UTF8&pageNumber=1&reviewerType=all_reviews&pageSize=100&sortBy=recent")
                        
                        soup2 = BeautifulSoup(r.text)

                        #extract the total number of pages
                        maxpage=1
                        list=soup2.find('ul', {'class':'a-pagination'})

                        if list!=None:
                            list=list.contents
                            maxpage=int(list[len(list)-2].text)                            
                        else:
                            maxpage=1
                            
                        for i in range(1,maxpage+1):
                            try:
                                
                                r=s.get(url=extract_href[0]+'/ref=cm_cr_getr_d_paging_btm_'+str(i)+'?ie=UTF8&pageNumber='+str(i)+'&reviewerType=all_reviews&pageSize=100&sortBy=recent')
                                count_page=0
                                if (r.status_code==200):
                                    soup2 = BeautifulSoup(r.text)
                                    # extract review text
                                    
                                    review=soup2.findAll('div', {'class': 'a-section review'})
                                    
                                    for rev in review:
                                        counter=counter+1
                                        soup2=BeautifulSoup(str(rev))
                                        count=(counter)
                                        star=(soup2.div.div.div.a.i.span.string[0])
                                        reviews=(soup2.div.div.div.contents[2].text)
                                        count_page+=1
                                        print "Review ",str(count_page)+" of page="+str(i)+"/ totalpages= "+str(maxpage)
                                        review_text = "".join([text.encode("utf8") for text in reviews])
                                        
                                        if export_ASIN==True:
                                            writer.writerow([count, product_val.asin ,int(star), ''.join(review_text.splitlines())])
                                        else:
                                            writer.writerow([count, int(star), ''.join(review_text.splitlines())])
                                else:
                                    print "Error: "
                                    print sys.exc_info()
                                    exit()
                            except:
                                print "Error: "
                                print sys.exc_info()
                                exit()
                    except:
                        print "Error #2... Retrying now..."
                        print sys.exc_info()
                        i=i-1                       
                except:
                    print "Error #1"
                    print sys.exc_info()
                    exit()            
                             

