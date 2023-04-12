from bs4 import BeautifulSoup
from bs4.element import Tag

def check(statement,soup:BeautifulSoup):
    try: 
        #code=compile(statement,"<string>", "exec")
        exec(statement,locals())
        result=eval(statement)
        return result
    except Exception as e:
        #raise e
        return False
    
def f_tags(soup:BeautifulSoup):
    maybe_tags=(
        r"""soup.find("meta",attrs=dict(property="og:description"))["content"]""",
        r"""soup.find("meta",attrs=dict(property="og:title"))["content"].split("|")[0].strip()""",
        r"""soup.find("title").text.split("|")[0].strip()"""
    )
    try:
        for i in maybe_tags:
            tags=check(i,soup)
            if (tags != False) and (isinstance(tags,str)) and (len(tags)>2):
                return tags
        return False
    except Exception as e:
        raise e
    
def f_link(soup:BeautifulSoup):
    maybe_link=(
        r"""soup.select('li > a.original-file-unchanged.highres-show[href$=".jpg"][id="highres-show"]')""",
        r"""soup.select('li > a.original-file-changed.highres-show[href$=".jpg"][id="highres-show"]')""",
        r"""soup.find_all("a",attrs={"class":"original-file-unchanged","id":"highres"})""",
        r"""soup.find_all("a",attrs={"class":"original-file-unchanged highres-show","id":"highres-show"})""",
        r"""soup.find_all("a",attrs={"class":"original-file-changed","id":"highres"})""",
        r"""soup.find_all("a",attrs={"class":"original-file-changed highres-show","id":"highres-show"})""",
        r"""soup.find_all("link",attrs={"rel":"image_src"})""",
        r"""soup.find_all("meta",attrs={"property":"og:image"})"""
    )
    try:
        for i in maybe_link:
            links=check(i,soup=soup)
            if links==False:
                continue
            if len(links) == 0:
                continue
            for link in links:
                try:
                    if isinstance(link,Tag) and (len(link['href']) > 35):
                        return link['href']
                except KeyError:
                    if isinstance(link,Tag) and (len(link['link']) > 35):
                        return link['link']
                except Exception:
                    continue
                
        return False
    except Exception as e:
        raise e
    
            
#test
""" async def main():

    async with AsyncClient(headers=headers) as client:
        host=r"https://konachan.com/post/show/308012/https://konachan.com/post/show/340778/140"
        re=await client.get(host)
        source=re.text

        tags_link=[]
        for param_features in ("lxml","html.parser","html5lib","html","html5","xml","lxml-xml"):
            soup=BeautifulSoup(source,features=param_features)
            tags=f_tags(soup)
            link=f_link(soup)
            if (tags != False) and (link != False):
                tags_link.append(tags)
                tags_link.append(link)
                break
            else:
                continue
        if len(tags_link)==2:
            return tuple(tags_link)
        else:
            return "寄" """
        
#r=asyncio.run(main())
#print(r)





