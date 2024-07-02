import os
import json
import pandas as pd
import re
import tqdm
import cn2an

pad_token = "<None>"
charge_text = "危害国家安全公共分裂煽动颠覆政权投敌叛变间谍为境外窃取、剌探收买非法提供秘密情报放火决水爆炸险物质以方失过破坏交通工具设施电力备易燃损组织领导参加恐怖资助活劫持航空器船只汽车暴及飞行广播视用信制造卖运输邮寄储存枪支弹药违规销售盗抢夺有私藏出租借携带管刀品重大事故铁路营肇责任劳程教育消防强令章冒作业型群众性不谎驾驶帮宣扬主义极端实生产伪劣商走妨对司企的理秩序金融诈骗税征侵犯知识扰乱市场意杀人致死亡伤奸猥亵侮辱妇女儿童拘禁绑架拐被诬告陷雇从搜查入住宅诽谤刑讯逼证虐待监民族仇恨歧版少数自由开拆隐匿毁弃件复选举干涉婚姻军遗中介员虚假明文淫幼残疾乞讨个息获未成年进反治体官迫护看聚哄占职务挪特定款敲勒索财经拒付酬（边）卫环源保贩毒引诱容留绍传秽阻碍执武装区充招摇撞接送合格兵部队印标志式服使专贪污受贿单位赂巨额来瞒罚没利影响滥玩忽守泄露徇枉裁判在押脱逃舞弊减释暂予移案券发票抵扣口退凭机关签订履同林木采伐许可染病批准土地低价让纵检植疫办偷越解救子避处学珍贵流仲食渎擅离转房属符医材农兽化肥种妆币稀普货废固止注册本抽清算会计帐簿类亲友牟折股披要背上益购换立构高贷吸债内幕编并期操汇向系据承兑洗钱卡集抗追缴欠增值于著誉声串倒律灭团居身份警绝料听照统无线社冲击所斗殴寻衅滋黑展包庇授游示威旗徽道门邪迷赌博控考试题答代替网络尸骨灰辩诉讼打庭窝赃置封冻结狱械掩饰得他名胜古迹赠掘址墓葬石脊椎档血应液疗节手术捕捞猎濒野狩矿点耕树原苗唆欺麻醉精神协音像表演或"

def sentence_clear(string):
    if re.search("，$",string):
        for i in re.finditer("。",string):
            span = i.span()
        string = string[:span[0]+1]
    return string

def file_check(file:dict):
    error = {"Defendant":[],"Procuratorate":[],"Defence":[],"Fact":[],"Conclusion":[],"Judgement":[],"Article":[],"Annotations":[]}
    for ele,info in file.items():
        if ele in ["Defendant","Procuratorate","Defence","Fact","Conclusion","Judgement"]:
            error[ele] = True if pad_token not in info else False
        elif ele in "Article":
            error[ele] = True if len(info) > 0 else False
        elif ele in "Annotations":
            error[ele] = True if len(info) > 0 else False

    return error

def read_file(path):
    file = {"Defendant":[],"Procuratorate":[],"Defence":[],"Fact":[],"Conclusion":[],"Judgement":[],"Article":[],"Annotations":[]}
    #checkpoint = {"d":True,"p":True,"l":True,"f":True,"c":True,"j":True}
    checkpoint = {"d":False,"p":False,"l":False,"f":False,"c":False,"j":False}
   
    # 文档抽取 {嫌疑人相关:str,控辩:str,涉案事实:str,法院认定:str,判决:str}
    with open(path,"r") as f:
        for line in f.readlines():
            if len(line.strip()) == 0:
                continue

            defendent,procuratorate,defence,fact,conclusion,judgement,article= None,None,None,None,None,None,None
            line = re.sub("\u3000","",line.strip())

            if (re.search("审\s*判\s*长",line.strip()) or re.search("如不服从*本判决",line.strip())) and len(file["Judgement"]) > 0:
                checkpoint["j"] = False
                break
            
            # 被告信息
            if re.search("被告",line.strip()) and not checkpoint["d"]:
                defendent = line.strip()

            # 控辩观点(检方，被告&辩护)
            if re.search("审理终结",line.strip()): 
                checkpoint["d"] = True
                continue
            
            if not checkpoint["p"] and not checkpoint["l"] and checkpoint["d"]:
                if not checkpoint["p"]:
                    procuratorate = line.strip()

                if re.search("人民检察院指控",line.strip()) or re.search("^公诉机关指控",line.strip()):
                    procuratorate = line.strip()
                    if re.search("公诉机关认为，",line.strip()):
                        spanwithprocuratorate = re.search("公诉机关认为，",procuratorate)
                        procuratorate = procuratorate[:spanwithprocuratorate.span()[0]]
                    if re.search("上述事实",line.strip()):
                        spanwithprocuratorate = re.search("上述事实",procuratorate)
                        procuratorate = procuratorate[:spanwithprocuratorate.span()[0]]
                    if re.search("上述指控",line.strip()):
                        spanwithprocuratorate = re.search("上述指控",procuratorate)
                        procuratorate = procuratorate[:spanwithprocuratorate.span()[0]]
                    if re.search("据此",line.strip()):
                        spanwithprocuratorate = re.search("据此",procuratorate)
                        procuratorate = procuratorate[:spanwithprocuratorate.span()[0]]
                    if re.search("针对",line.strip()):
                        spanwithprocuratorate = re.search("针对",procuratorate)
                        procuratorate = procuratorate[:spanwithprocuratorate.span()[0]]
                    try:
                        if re.search("人民检察院指控",line.strip()):
                            spanwithprocuratorate = re.search("人民检察院指控[：，]*",procuratorate)
                            procuratorate = procuratorate[spanwithprocuratorate.end():] 
                        elif re.search("公诉机关指控",line.strip()):
                            spanwithprocuratorate = re.search("^公诉机关指控[称]*[：，]*",procuratorate)
                            procuratorate = procuratorate[spanwithprocuratorate.end():]
                    except Exception as E:
                        procuratorate = None
                    if len(procuratorate.strip()) < 10:
                        procuratorate = None 
                
                if re.search("^公诉机关",line.strip()) and len(file["Procuratorate"]) > 0:
                    procuratorate = None
                if re.search("公诉机关认为，",line.strip()) and len(file["Procuratorate"]) > 0:
                    procuratorate = None
                if re.search("公诉机关提供，",line.strip()) and len(file["Procuratorate"]) > 0:
                    procuratorate = None
                if re.search("上述事实",line.strip()) and len(file["Procuratorate"]) > 0:
                    procuratorate = None
                if re.search("上述指控",line.strip()) and len(file["Procuratorate"]) > 0:
                    procuratorate = None
                if re.search("认定上述指控",line.strip()) and len(file["Procuratorate"]) > 0:
                    procuratorate = None
                if re.search("针对",line.strip()) and len(file["Procuratorate"]) > 0:
                    procuratorate = None
                if re.search("^对于",line.strip()) and len(file["Procuratorate"]) > 0:
                    procuratorate = None
                if re.search("刑法",line.strip()) and len(file["Procuratorate"]) > 0:
                    procuratorate = None    

                if re.search("^被告人.{0,10}[对辩称]+",line.strip()) and checkpoint["d"]:
                    defence = line.strip()
                if re.search("^上诉人.{0,10}[对辩称]+",line.strip()) and checkpoint["d"]:
                    defence = line.strip()
                if re.search("辩护人.{0,10}[对辩称]*",line.strip()) and checkpoint["d"]:
                    defence = line.strip()
                if checkpoint["p"] and not checkpoint["l"]:
                    defence = line.strip()
                #elif not checkpoint["l"] and not defence:
                #    defence = line.strip()

            # 涉案事实
            if checkpoint["p"] and checkpoint["l"] and not checkpoint["f"]:
                fact = line.strip()
            if re.search("审理查明",line.strip()) and not checkpoint["f"]:
                fact = line.strip()
                if re.search("上述事实",fact):
                    factwithspan = re.search("上述事实",fact)
                    fact = fact[factwithspan.end():]
                    
                if re.search("审理查明",fact):
                    factwithspan = re.search("审理查明",fact)
                    fact = fact[factwithspan.end():]

                if re.search("^：",fact) or re.search("^，",fact):
                    fact = fact[1:].strip()
                                     
            if re.search("^上述事实",line.strip()) and len(file["Fact"]) > 0:
                fact = None
            if re.search("^上述证据",line.strip()) and len(file["Fact"]) > 0:
                fact = None
            if re.search("^对于",line.strip()) and len(file["Fact"]) > 0:
                fact = None

            if fact is not None:
                fact = fact if len(fact) > 10 else None

            # 法院观点/法条 & 判决
            if re.search("[\s\u3000]*本院认为",line.strip()) and not checkpoint["c"]:
                if re.search("判决如下",line.strip()):
                    startwithJudgement = re.search("判决如下",line.strip())
                    conclusion,judgement = line.strip()[:startwithJudgement.span()[0]],line.strip()[startwithJudgement.span()[0]:]
                    #conclusion = sentence_clear(conclusion)
                else:
                    conclusion = line.strip()

                if re.search("依照",conclusion):
                    startwithArticle = re.search("依照",conclusion)
                    conclusion,article = conclusion[:startwithArticle.span()[0]], conclusion[startwithArticle.span()[1]+1:]
                    article = re.sub("之规定，","",article)
                elif re.search("根据《中华人民共和国刑法》",conclusion):
                    startwithArticle = re.search("根据《中华人民共和国刑法》",conclusion)
                    conclusion,article = conclusion[:startwithArticle.span()[0]], conclusion[startwithArticle.span()[1]+1:]
                    article = re.sub("之规定，","",article)

            # 判决
            if checkpoint["c"] and not checkpoint["j"]:
                judgement = line.strip()
            
            if re.search("判决如下",line.strip()) and not checkpoint["j"]:
                startwithJudgement = re.search("判决如下",line.strip())
                judgement = line.strip()[startwithJudgement.span()[0]:]

                if re.search("依照",line.strip()):
                    startwithArticle = re.search("依照",line.strip())
                    article = line.strip()[startwithArticle.span()[0]:startwithJudgement.span()[0]]
                    article = re.sub("之规定，","",article)
                elif re.search("依据《中华人民共和国刑法》",line.strip()):
                    startwithArticle = re.search("依据《中华人民共和国刑法》",line.strip())
                    article = line.strip()[startwithArticle.span()[0]:startwithJudgement.span()[0]]
                    article = re.sub("之规定，","",article)
                    #article = re.sub("的规定，","",article)
                elif re.search("根据《中华人民共和国刑法》",line.strip()):
                    startwithArticle = re.search("根据《中华人民共和国刑法》",line.strip())
                    article = line.strip()[startwithArticle.span()[0]:startwithJudgement.span()[0]]
                    article = re.sub("之规定，","",article)
                             
            # 填充file
            if article:
                file["Article"].append(article)   
            if not checkpoint["c"] and conclusion:
                checkpoint["d"] = True
                checkpoint["p"] = True
                checkpoint["l"] = True
                checkpoint["f"] = True
                file["Conclusion"].append(conclusion)            
            if not checkpoint["j"] and judgement:
                checkpoint["c"] = True  # 判决与法院观点会出现在同一段落
                file["Judgement"].append(judgement)

            if not checkpoint["f"] and fact:
                checkpoint["l"] = True
                checkpoint["p"] = True
                checkpoint["d"] = True  # 如被告无异议，可能不会出现控辩
                file["Fact"].append(fact)
            if not checkpoint["l"] and defence:
                checkpoint["p"] = True
                file["Defence"].append(defence)
            if not checkpoint["p"] and procuratorate:
                checkpoint["d"] = True
                file["Procuratorate"].append(procuratorate)
      
            if not checkpoint["d"] and defendent:
                file["Defendant"].append(defendent)

    # 补全缺失 & 法条后处理
    for ele,info in file.items():
        if "Article" in ele:
            articles = []
            articlespan = re.search("《中华人民共和国刑法》[零一二三四五六七八九十百第条款、，]{1,100}","".join(info))
            if articlespan:
                #articlespan = articlespan.span()
                articlespan = "".join(info)[articlespan.span()[0]+11:articlespan.span()[1]]
                for span in re.finditer("第[零一二三四五六七八九十百]{1,5}条",articlespan):
                    if span:
                        idx = span.span()
                        articles.append(cn2an.cn2an(articlespan[idx[0]+1:idx[1]-1]))
            file[ele] = articles  # 如正则失败，则将“Article”的值修改为空数组
        elif "Judgement" in ele:
            annotations = []
            for text in info:
                '''
                被告人姓名name
                罪名charge。特别的，若被告人无罪，则charge值为无罪
                判罚种类penalty分为拘役，管制，有期，无期，死刑与免于刑事处罚，共6类
                (拘役，管制，有期对应刑期出现；无期，死刑与免于刑事处罚时不会出现刑期)
                刑期imprisonment。单位为月
                样本一般写法：
                被告人张三犯非法采矿罪，判处有期徒刑一年六个月
                '''
                name,charge,imprisonment,penalty = None,[],None,None 
                # 姓名
                #name = re.search("被告人.*犯",text)
                if re.search("被告人.{1,5}犯",text) or re.search("被告人.{1,5}无罪",text):
                    if re.search("被告人.{1,5}犯",text):
                        idx = re.search("被告人.{1,5}犯",text).span()
                        name = text[idx[0]+3:idx[1]-1]
                    else:
                        idx = re.search("被告人.{1,5}无罪",text).span()
                        name = text[idx[0]+3:idx[1]-2]
                # 罪名
                charge = re.search("犯[%s]*罪"%(charge_text),text)
                if charge:
                    idx = charge.span()
                    charge = text[idx[0]+1:idx[1]-1]
                # 无罪 & 免于 & 死刑 & 无期
                if re.search("被告人.*无罪",text):
                    penalty = "无罪"
                    imprisonment = 0
                    annotations.append({"criminals":name,"annotation":[{"charge":"","penalty":penalty,"imprisonment":imprisonment}],"penalty":penalty,"imprisonment":imprisonment})  
                elif re.search("被告人.*免予刑事处罚",text):
                    penalty = "免予刑事处罚"
                    imprisonment = 0
                    annotations.append({"criminals":name,"annotation":[{"charge":charge,"penalty":penalty,"imprisonment":imprisonment}],"penalty":penalty,"imprisonment":imprisonment})  
                elif re.search("被告人.*判处死刑",text):
                    penalty = "死刑"
                    imprisonment = 0
                    annotations.append({"criminals":name,"annotation":[{"charge":charge,"penalty":penalty,"imprisonment":imprisonment}],"penalty":penalty,"imprisonment":imprisonment})  
                elif re.search("被告人.*判处无期徒刑",text):
                    penalty = "无期徒刑"
                    imprisonment = 0
                    annotations.append({"criminals":name,"annotation":[{"charge":charge,"penalty":penalty,"imprisonment":imprisonment}],"penalty":penalty,"imprisonment":imprisonment})  
                # 有期徒刑 & 拘役 & 管制
                elif name:
                    annotation = []
                    # 不同罪名判罚
                    imprisonment,penalty = 0, ""
                    for subtext in re.findall("犯[%s]*罪，{0,1}判处[有期徒刑拘役管制]{2,4}[零一二三四五六七八九十]{1,3}年*零*[零一二三四五六七八九十]{0,2}个*月*"%charge_text,text):
                        idx = re.search("犯[%s]*罪"%charge_text,text).span()
                        charge = text[idx[0]+1:idx[1]-1]
                        if re.search("判处有期徒刑[零一二三四五六七八九十]{1,3}年零*[零一二三四五六七八九十]{1,2}个月",subtext):
                            idx = re.search("判处有期徒刑[零一二三四五六七八九十]{1,3}年零*[零一二三四五六七八九十]{1,2}个月",subtext).span()
                            imprisonment = subtext[idx[0]+6:idx[1]-2]
                            year = re.search("[零一二三四五六七八九十]{1,3}年",imprisonment).span()
                            year = imprisonment[year[0]:year[1]-1]
                            month = re.search("年零*[零一二三四五六七八九十]{1,2}",imprisonment).span()
                            month = imprisonment[month[0]+1:]
                            if re.search("^零",month):
                                month = re.sub("^零","",month)
                            year,month = cn2an.cn2an(year),cn2an.cn2an(month)
                            penalty = "有期徒刑"
                            imprisonment = int(year) * 12 + int(month)
                        elif re.search("判处有期徒刑[零一二三四五六七八九十]{1,3}年",subtext):
                            idx = re.search("判处有期徒刑[零一二三四五六七八九十]{1,3}年",subtext).span()
                            year = subtext[idx[0]+6:idx[1]-1]
                            year = cn2an.cn2an(year)
                            penalty = "有期徒刑"
                            imprisonment = int(year) * 12
                        elif re.search("判处有期徒刑[零一二三四五六七八九十]{1,3}个月",subtext):
                            idx = re.search("判处有期徒刑[零一二三四五六七八九十]{1,3}个月",subtext).span()
                            month = subtext[idx[0]+6:idx[1]-2]
                            month = cn2an.cn2an(month)
                            penalty = "有期徒刑"
                            imprisonment = int(month)
                        elif re.search("判处拘役[零一二三四五六七八九十]{1,3}年零*[零一二三四五六七八九十]{1,2}个月",subtext):
                            idx = re.search("判处拘役[零一二三四五六七八九十]{1,3}年零*[零一二三四五六七八九十]{1,2}个月",subtext).span()
                            imprisonment = subtext[idx[0]+4:idx[1]-2]
                            year = re.search("[零一二三四五六七八九十]{1,3}年",imprisonment).span()
                            year = imprisonment[year[0]:year[1]-1]
                            month = re.search("年零*[零一二三四五六七八九十]{1,2}",imprisonment).span()
                            month = imprisonment[month[0]+1:]
                            year,month = cn2an.cn2an(year),cn2an.cn2an(month)
                            if re.search("^零",month):
                                month = re.sub("^零","",month)
                            penalty = "拘役"
                            imprisonment = int(year) * 12 + int(month)
                        elif re.search("判处拘役[零一二三四五六七八九十]{1,3}年",subtext):
                            idx = re.search("判处拘役[零一二三四五六七八九十]{1,3}年",subtext).span()
                            year = subtext[idx[0]+4:idx[1]-1]
                            year = cn2an.cn2an(year)
                            penalty = "拘役"
                            imprisonment = int(year) * 12
                        elif re.search("判处拘役[零一二三四五六七八九十]{1,3}个月",subtext):
                            idx = re.search("判处拘役[零一二三四五六七八九十]{1,3}个月",subtext).span()
                            month = subtext[idx[0]+4:idx[1]-2]
                            month = cn2an.cn2an(month)
                            penalty = "拘役"
                            imprisonment = int(month)
                        elif re.search("判处管制[零一二三四五六七八九十]{1,3}年零*[零一二三四五六七八九十]{1,2}个月",subtext):
                            idx = re.search("判处管制[零一二三四五六七八九十]{1,3}年零*[零一二三四五六七八九十]{1,2}个月",subtext).span()
                            imprisonment = subtext[idx[0]+4:idx[1]-2]
                            year = re.search("[零一二三四五六七八九十]{1,3}年",imprisonment).span()
                            year = imprisonment[year[0]:year[1]-1]
                            month = re.search("年零*[零一二三四五六七八九十]{1,2}",imprisonment).span()
                            month = imprisonment[month[0]+1:]
                            if re.search("^零",month):
                                month = re.sub("^零","",month)
                            year,month = cn2an.cn2an(year),cn2an.cn2an(month)
                            penalty = "管制"
                            imprisonment = int(year) * 12 + int(month)
                        elif re.search("判处管制[零一二三四五六七八九十]{1,3}年",subtext):
                            idx = re.search("判处管制[零一二三四五六七八九十]{1,3}年",subtext).span()
                            year = subtext[idx[0]+4:idx[1]-1]
                            year = cn2an.cn2an(year)
                            penalty = "管制"
                            imprisonment = int(year) * 12
                        elif re.search("判处管制[零一二三四五六七八九十]{1,3}个月",subtext):
                            idx = re.search("判处管制[零一二三四五六七八九十]{1,3}个月",subtext).span()
                            month = subtext[idx[0]+4:idx[1]-2]
                            month = cn2an.cn2an(month)
                            penalty = "管制"
                            imprisonment = int(month)
                        if imprisonment and penalty:
                            annotation.append({"charge":charge,"penalty":penalty,"imprisonment":imprisonment})
                    
                    # 最终执行刑期
                    if re.search("决定合*并*执行有期徒刑[零一二三四五六七八九十]{1,3}年零*[零一二三四五六七八九十]{1,2}个月",text):
                        idx = re.search("执行有期徒刑[零一二三四五六七八九十]{1,3}年零*[零一二三四五六七八九十]{1,2}个月",text).span()
                        imprisonment = text[idx[0]+6:idx[1]-2]
                        year = re.search("[零一二三四五六七八九十]{1,3}年",imprisonment).span()
                        year = imprisonment[year[0]:year[1]-1]
                        month = re.search("年零*[零一二三四五六七八九十]{1,2}",imprisonment).span()
                        month = imprisonment[month[0]+1:]
                        if re.search("^零",month):
                            month = re.sub("^零","",month)
                        year,month = cn2an.cn2an(year),cn2an.cn2an(month)
                        penalty = "有期徒刑"
                        imprisonment = int(year) * 12 + int(month)
                    elif re.search("决定合*并*执行有期徒刑[零一二三四五六七八九十]{1,3}年",text):
                        idx = re.search("执行有期徒刑[零一二三四五六七八九十]{1,3}年",text).span()
                        year = text[idx[0]+6:idx[1]-1]
                        year = cn2an.cn2an(year)
                        penalty = "有期徒刑"
                        imprisonment = int(year) * 12
                    elif re.search("决定合*并*执行有期徒刑[零一二三四五六七八九十]{1,3}个月",text):
                        idx = re.search("执行有期徒刑[零一二三四五六七八九十]{1,3}个月",text).span()
                        month = text[idx[0]+6:idx[1]-2]
                        month = cn2an.cn2an(month)
                        penalty = "有期徒刑"
                        imprisonment = int(month)
                    elif re.search("决定合*并*执行拘役[零一二三四五六七八九十]{1,3}年零*[零一二三四五六七八九十]{1,2}个月",text):
                        idx = re.search("执行拘役[零一二三四五六七八九十]{1,3}年零*[零一二三四五六七八九十]{1,2}个月",text).span()
                        imprisonment = text[idx[0]+4:idx[1]-2]
                        year = re.search("[零一二三四五六七八九十]{1,3}年",imprisonment).span()
                        year = imprisonment[year[0]:year[1]-1]
                        month = re.search("年零*[零一二三四五六七八九十]{1,2}",imprisonment).span()
                        month = imprisonment[month[0]+1:]
                        year,month = cn2an.cn2an(year),cn2an.cn2an(month)
                        if re.search("^零",month):
                            month = re.sub("^零","",month)
                        penalty = "拘役"
                        imprisonment = int(year) * 12 + int(month)
                    elif re.search("决定合*并*执行拘役[零一二三四五六七八九十]{1,3}年",text):
                        idx = re.search("执行拘役[零一二三四五六七八九十]{1,3}年",text).span()
                        year = text[idx[0]+4:idx[1]-1]
                        year = cn2an.cn2an(year)
                        penalty = "拘役"
                        imprisonment = int(year) * 12
                    elif re.search("决定合*并*执行拘役[零一二三四五六七八九十]{1,3}个月",text):
                        idx = re.search("执行拘役[零一二三四五六七八九十]{1,3}个月",text).span()
                        month = text[idx[0]+4:idx[1]-2]
                        month = cn2an.cn2an(month)
                        penalty = "拘役"
                        imprisonment = int(month)
                    elif re.search("决定合*并*执行管制[零一二三四五六七八九十]{1,3}年零*[零一二三四五六七八九十]{1,2}个月",text):
                        idx = re.search("执行管制[零一二三四五六七八九十]{1,3}年零*[零一二三四五六七八九十]{1,2}个月",text).span()
                        imprisonment = text[idx[0]+4:idx[1]-2]
                        year = re.search("[零一二三四五六七八九十]{1,3}年",imprisonment).span()
                        year = imprisonment[year[0]:year[1]-1]
                        month = re.search("年零*[零一二三四五六七八九十]{1,2}",imprisonment).span()
                        month = imprisonment[month[0]+1:]
                        if re.search("^零",month):
                            month = re.sub("^零","",month)
                        year,month = cn2an.cn2an(year),cn2an.cn2an(month)
                        penalty = "管制"
                        imprisonment = int(year) * 12 + int(month)
                    elif re.search("决定合*并*执行管制[零一二三四五六七八九十]{1,3}年",text):
                        idx = re.search("执行管制[零一二三四五六七八九十]{1,3}年",text).span()
                        year = text[idx[0]+4:idx[1]-1]
                        year = cn2an.cn2an(year)
                        penalty = "管制"
                        imprisonment = int(year) * 12
                    elif re.search("决定合*并*执行管制[零一二三四五六七八九十]{1,3}个月",text):
                        idx = re.search("执行管制[零一二三四五六七八九十]{1,3}个月",text).span()
                        month = text[idx[0]+4:idx[1]-2]
                        month = cn2an.cn2an(month)
                        penalty = "管制"
                        imprisonment = int(month)
                    elif re.search("决定合*并*执行死刑",text):
                        penalty = "死刑"
                        imprisonment = 0
                    elif re.search("决定合*并*执行无期徒刑",text):
                        penalty = "无期徒刑"
                        imprisonment = 0
                    
                    annotations.append({"criminals":name,"annotation":annotation,"penalty":penalty,"imprisonment":imprisonment})
            file["Annotations"] = annotations
        else:
            if ele in ["Defendant","Procuratorate","Defence","Fact","Conclusion","Judgement"]:
                file[ele] = "\n".join(info) if len(info) > 0 else pad_token

    return file

def read_files(path,error_log_path="./error_file.tsv"):
    files = []
    error_files = []

    # 读取文件目录
    df = pd.read_csv("./codekey.txt",dtype={"count_id":str})
    id2charge = {str(k):v for k,v in zip(df["count_id"],df["count_name"])}
    ids = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]

    
    # 读取文件
    print("read files..")
    debug_files = []
    for i,id in enumerate(ids):
        print(str(i) + "、Dir: " + id)
        e_counter = []
        for file in tqdm.tqdm(os.listdir(os.path.join(path,id))):
            try:
                corpus = read_file(os.path.join(path,id,file))
                corpus["id"] = os.path.join(id,file)
                corpus["charge"] = id2charge[id]
                files.append(corpus)
            except Exception as e:
                corpus = {"Defendant":"<None>","Procuratorate":"<None>","Defence":"<None>","Fact":"<None>","Conclusion":"<None>","Judgement":"<None>","charge":"<None>","Article":[],"Annotations":[],"id":os.path.join(id,file)}
                e_counter.append(os.path.join(id,file))
            
            # 检查错误
            error = file_check(corpus)
            if False in error.values():
                error["id"] = "+".join([id,file])
                error_files.append(error)
        
        # 测试代码，后期需要删
        if len(os.listdir(os.path.join(path,id))) > 0:
            print("per: " + str(len(e_counter)/len(os.listdir(os.path.join(path,id)))))
            print("num: " + str(len(e_counter)))
            debug_files += e_counter
    
    # 保存错误文档记录
    error_files = pd.DataFrame(error_files)
    error_files.to_csv(error_log_path,sep="\t")

    return files

def save_files(files:list,output_path="/home/sda/zhangyuanyu/workspace/Judgment/data/corpus.jsonl"):
    print("save files..")
    with open(output_path,"w") as f:
        for corpus in tqdm.tqdm(files):
            f.write(json.dumps(corpus,ensure_ascii=False))
            f.write("\n")

def main():
    files_path = "./doc"
    files = read_files(files_path)
    save_files(files)

if __name__ == "__main__":
    main()
