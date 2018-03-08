# 脉脉爬虫

脉脉爬虫

        -Maimai

        　　　└ Maiaddfriend_spider
　　　
        　　　└ mysqlpipelines
　　　
        　　　└ spiders  
　　　
        　　　...
        　　　...   
　　　
　　　

python3.6

####设置账号

*（在cookies.py 中设置）*

        ACCOUNT = [
        
            {
            
                'm': '****手机号*****',
                
                'p': '**** 密码 *****',
                
                'to': None,
                
                'pa': '+86'
                
            },
            
        ]

####执行爬去基本信息：

        scrapy crawl maimai

####每天定时执行添加好友信息 & 每天验证申请的好友是否通过，通过的保存email到数据库中：

*（在Maiaddfriend_spide目录下， 默认每天添加好友数量5个，增加添加好友数量请修改check_pass.py 下 count变量）*

        python check_pass.py
