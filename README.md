# LegalLJP
StageLJP: A Multi-Stage Dataset for Legal Judgment Prediction
We introduce a multi-stage Chinese legal judgment prediction dataset. It encompasses approximately one million documents and includes various types of labels such as court opinions, relevant laws, charges, and prison term.

## Dataset Structure
We processed the original text into the following structured representation.

Defendant:'被告人杜某甲，性别：××，××族，学生。2014年3月21日因涉嫌犯放火罪被遵化市公安局刑事拘留，同年4月2日经遵化市公安局决定取保候审。2014年10月28日经本院决定取保候审。'

Procuratorate: '2013年12月25日，被告人杜某甲因不满父母离婚，在其父母去民政局办理离婚手续期间，将自家东屋内海绵垫点燃，致使屋内其他易燃物品燃烧，造成整个房屋及大部分物品被烧毁。经遵化市价格鉴定中心认定：被烧毁物品价值为46700元。'

Defence: '被告人杜某甲辩称，她家被烧的火不是她放的，2014年12月25日那天其在遵化市金源超市和刘某在一起未在家中，她父亲因对其不满意到公安机关说是她放的火，她曾对公安干警提出火不是她放的，由于公安干警吓唬她，就说是自己放的火；另外杜某乙没在家，不能作为证人。'

Fact: '2013年12月25日，被告人杜某甲因不满其父母离婚，在其父母离家去民政局办理离婚手续后，遂将自家东屋内海绵垫点燃，并把没叠起的被子盖到点燃的海绵垫子上，致使屋内易燃物品燃烧，起初造成该房屋东屋起火，被本村村民扑灭后，约过二十分钟，该房屋再次起火，后被村民和消防队扑灭，造成整个房屋及大部分物品被烧毁。经遵化市价格鉴定中心鉴定，被烧毁物品的价格为46700元。\n审理中，被告人杜某甲的父亲杜某戊、母亲孟某乙均表示不要求被告人杜某甲赔偿，并请求对被告人杜某甲从轻处罚。\n被告人杜某甲的庭前供述，那天早晨七、八点，其父母去民政局办离婚手续，其不愿意，就从东屋柜上找到一个打火机，到西屋点她奶用的褥子，没点着，就到东屋把海绵垫子点着了，把没叠起的被盖到海绵垫子上，后就从自家北面的大门走出，并给其父亲打电话，告之把房子点着了，后来又坐车到遵化和刘某在一起，并将点火的事告诉了刘某和杜某乙飞。\n被害人孟某乙陈述，证实杜某甲向证人说过用打火机将东屋炕上的被子点着了。\n被害人杜某戊陈述，证明杜某甲那天给证人打电话称把房子点着了。\n证人杜某乙证言，证明被烧物品在购买时的价格。\n证人杜某乙飞证言，证明杜某甲曾某证人打电话说把房子点着了。\n证人刘某证言，证明杜某甲对证人说因她爸、妈闹离婚，把房子点着了。\n证人杜某丁证言，证明杜某戊和他说过是杜某甲将房子点着了。\n8、证人陈某乙证言，证明杜某戊他们两家的房紧挨着，那天证人帮忙往杜某戊院里用水桶递水，第一次把火扑灭后，证人进屋看见东屋炕上的被子烧了，窗帘也烧毁了，随后他就回家了，过了十多分钟，杜某甲家又着火了，后来和消防队的人一起把火彻底扑灭。\n9、证人陈某甲证言，证明那天证人看见杜某戊家着火（听陈某乙说是第二次着火）后，开始救火，并打了报警电话。\n10、证人白某证言，证明那天杜某戊家第一次着火被扑灭后，过十多分钟又着了，证人和兰某、陈某乙等人一起救火，不知道第二次怎么着的。\n11、证人兰某证言，证明那天杜某戊家着火后，证人第一个进屋的，杜家当时没人，火从东屋西头的炕上着起来，陈某乙他俩开始灭火，后来杜某戊两口子回来了，把炕上、窗框上的火扑灭后其就回家了，过了二十分钟，杜家房顶又着火了，后来火被扑灭了。\n12、证人王某证言，证明那天证人看见杜某甲气冲冲的往北走，就追上她，用电动车把杜某甲带到证人家。中午回来时见杜某甲走了。\n13、遵化市公安局现场勘验笔录及现场照片，证实房屋被烧毁的状况。\n14、财产损失清单和遵化市价格鉴证中心价格鉴证报告，被烧毁物品的价格为46700元。\n15、被害人杜某戊、孟某乙的申请，请求对杜某甲从轻处罚。\n16、遵化市公安局的情况说明，杜某甲出生于1995年6月5日，在遵化市堡子店中学被抓获。'

Conclusion:’ 本院认为，被告人杜某甲因不满其父母离婚，故意将自家东屋内的物品点燃造成房屋及物品被烧毁，危害公共安全，其行为已构成放火罪，应依法惩处。遵化市人民检察院指控被告人杜某甲犯放火罪事实清楚，证据确实、充分，指控的罪名成立。被告人杜某甲庭审中翻供，但不能合理说明翻供理由，其庭前供述与其他证据相互印证，本院采信其庭前供述；其提出的未放火点燃物品的辩护意见，证据不足，本院不予采纳。被告人杜某甲系初犯，尚未造成严重损失，且被害人杜某戊、孟某乙表示对其谅解，可酌情从轻处罚。'

Article: [114, 61]

Annotations:

--'criminals': '杜某甲',
 
--'annotation': [{'charge': '放火', 'penalty': '有期徒刑', 'imprisonment': 36}],
   
--'penalty': '有期徒刑',
   
--'imprisonment': 36

The specific meanings of the annotations are explained as follows:

Defendant: Information related to the defendant

Procuratorate: Facts of the accusation

Defence: Statements and arguments of the defendant and defense attorney

Fact: Facts recognized by the court after review, including evidence descriptions and witness testimonies

Conclusion: Court's opinion. The court's opinion on the above paragraphs, usually serving as the basis for the judgment

Article: Articles involved in the judgment result

Annotations: Structured representation of the judgment result，where：

--criminals: Alias for the defendant's name
    
--penalty: Decided penalty
    
--imprisonment: Decided imprisonment term (in months)
    
--annotation: Penalty based on the charge, including —— charge: Alleged crime，penalty: Penalty，imprisonment: Imprisonment term
        
A single defendant may be accused of multiple charges, so the annotation may include multiple penalties.

## Processing of Original Corpus

prompt.py: Convert Corpus to Fixed QA Structure (To facilitate training, the question-answer structure follows the [Firefly](https://github.com/yangjianxin1/Firefly))

segment.py: Random sampling of training and testing sets from the raw data.

sampling.py: Balancing the training set. To retain as many samples as possible, we set a minimum quantity threshold for each crime and retained 90% of the samples. The number of retained samples can be adjusted via the "--quantile" parameter.




