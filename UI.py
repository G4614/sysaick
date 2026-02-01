import os
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
import json

app = Flask(__name__, static_folder='static')
app.secret_key = 'your-secret-key-here'

# 检验项目分类数据
test_categories = [
    {"id": "basic", "name": "基本信息提供", "icon": "info-circle"},
    {"id": "biochemical", "name": "生化指标", "icon": "flask"},
    {"id": "immune", "name": "免疫指标", "icon": "shield-alt"},
    {"id": "clinical", "name": "临检指标", "icon": "stethoscope"},
    {"id": "microbiology", "name": "微生物指标", "icon": "virus"},
    {"id": "molecular", "name": "分子指标", "icon": "dna"},
    {"id": "ct", "name": "CT图像", "icon": "x-ray"},
    {"id": "mr", "name": "MR图像", "icon": "magnet"},
    {"id": "ultrasound", "name": "彩超", "icon": "wave-square"}
]

# 模拟数据
sample_data = {
    "basic": [
        {"id": 1, "name": "血常规", "description": "检查血液中各种细胞成分的数量和比例", "recommendation": "健康体检必检项目"},
        {"id": 2, "name": "尿常规", "description": "检查尿液中的各种成分", "recommendation": "泌尿系统疾病筛查"}
    ],
    "biochemical": [
        {"id": 3, "name": "肝功能", "description": "检查肝脏功能相关指标", "recommendation": "肝脏疾病筛查、药物副作用监测"},
        {"id": 4, "name": "肾功能", "description": "检查肾脏功能相关指标", "recommendation": "肾脏疾病筛查、高血压患者监测"}
    ],
    "immune": [
        {"id": 5, "name": "免疫球蛋白", "description": "检查免疫系统功能", "recommendation": "免疫功能评估、自身免疫性疾病筛查"},
        {"id": 6, "name": "肿瘤标志物", "description": "检查肿瘤相关标志物", "recommendation": "肿瘤筛查、治疗效果监测"}
    ],
    "clinical": [
        {"id": 7, "name": "凝血功能", "description": "检查血液凝固功能", "recommendation": "手术前评估、出血性疾病筛查"},
        {"id": 8, "name": "血沉", "description": "检查红细胞沉降率", "recommendation": "炎症性疾病筛查"}
    ],
    "microbiology": [
        {"id": 9, "name": "细菌培养", "description": "检测病原体", "recommendation": "感染性疾病诊断"},
        {"id": 10, "name": "药敏试验", "description": "检测细菌对药物的敏感性", "recommendation": "指导抗生素使用"}
    ],
    "molecular": [
        {"id": 11, "name": "PCR检测", "description": "检测特定DNA或RNA序列", "recommendation": "病原体检测、基因变异分析"},
        {"id": 12, "name": "基因测序", "description": "分析基因序列", "recommendation": "遗传病诊断、肿瘤基因检测"}
    ],
    "ct": [
        {"id": 13, "name": "胸部CT", "description": "检查胸部器官结构", "recommendation": "肺部疾病筛查、肿瘤诊断"},
        {"id": 14, "name": "腹部CT", "description": "检查腹部器官结构", "recommendation": "腹部肿瘤筛查、急腹症诊断"}
    ],
    "mr": [
        {"id": 15, "name": "头颅MRI", "description": "检查脑部结构", "recommendation": "脑血管疾病、脑肿瘤诊断"},
        {"id": 16, "name": "脊柱MRI", "description": "检查脊柱结构", "recommendation": "脊柱疾病、神经压迫诊断"}
    ],
    "ultrasound": [
        {"id": 17, "name": "腹部彩超", "description": "检查腹部器官", "recommendation": "肝脏、胆囊、胰腺疾病筛查"},
        {"id": 18, "name": "心脏彩超", "description": "检查心脏结构和功能", "recommendation": "心脏疾病诊断、心功能评估"}
    ]
}

# 年龄段分组数据
age_groups = {
    "青少年": {"range": "18岁以下", "min": 0, "max": 18},
    "青壮年": {"range": "18-35岁", "min": 18, "max": 35},
    "中青年": {"range": "36-50岁", "min": 36, "max": 50},
    "老年": {"range": "51岁以上", "min": 51, "max": 150}
}

# 不同年龄段的推荐体检套餐数据
recommended_packages = {
    "青少年": [
        {"id": 1, "name": "青少年基础套餐", "description": "适合青少年的基础体检项目", "items": ["血常规", "尿常规", "肝功能", "肾功能", "心电图"]},
        {"id": 2, "name": "青少年全面套餐", "description": "适合青少年的全面体检项目", "items": ["血常规", "尿常规", "肝功能", "肾功能", "心电图", "胸部X线", "腹部B超", "微量元素"]}
    ],
    "青壮年": [
        {"id": 3, "name": "青壮年基础套餐", "description": "适合青壮年的基础体检项目", "items": ["血常规", "尿常规", "肝功能", "肾功能", "血脂", "血糖", "心电图"]},
        {"id": 4, "name": "青壮年全面套餐", "description": "适合青壮年的全面体检项目", "items": ["血常规", "尿常规", "肝功能", "肾功能", "血脂", "血糖", "心电图", "胸部CT", "腹部彩超", "甲状腺彩超"]}
    ],
    "中青年": [
        {"id": 5, "name": "中青年基础套餐", "description": "适合中青年的基础体检项目", "items": ["血常规", "尿常规", "肝功能", "肾功能", "血脂", "血糖", "心电图", "肿瘤标志物"]},
        {"id": 6, "name": "中青年全面套餐", "description": "适合中青年的全面体检项目", "items": ["血常规", "尿常规", "肝功能", "肾功能", "血脂", "血糖", "心电图", "肿瘤标志物", "胸部CT", "腹部彩超", "甲状腺彩超", "心脏彩超"]}
    ],
    "老年": [
        {"id": 7, "name": "老年基础套餐", "description": "适合老年的基础体检项目", "items": ["血常规", "尿常规", "肝功能", "肾功能", "血脂", "血糖", "心电图", "肿瘤标志物", "骨密度"]},
        {"id": 8, "name": "老年全面套餐", "description": "适合老年的全面体检项目", "items": ["血常规", "尿常规", "肝功能", "肾功能", "血脂", "血糖", "心电图", "肿瘤标志物", "骨密度", "胸部CT", "腹部彩超", "甲状腺彩超", "心脏彩超", "头颅MRI"]}
    ]
}

# 基础疾病选项
basic_diseases = [
    "高血压", "糖尿病", "冠心病", "脑血管疾病", "慢性肾病",
    "慢性肝病", "甲状腺疾病", "肿瘤病史", "自身免疫性疾病", "其他"
]

# 不良嗜好选项
bad_habits = [
    "吸烟", "喝酒", "熬夜", "缺乏运动", "不健康饮食"
]

# 医院价格数据（Mock Data）
hospital_prices = {
    "血常规": [
        {"name": "中山大学孙逸仙纪念医院", "type": "public", "distance": "1.2km", "price": 25, "rating": 4.9, "department": "检验科", "wait_time": "30分钟", "booking_status": "可预约"},
        {"name": "广东省人民医院", "type": "public", "distance": "2.5km", "price": 28, "rating": 4.8, "department": "检验科", "wait_time": "45分钟", "booking_status": "可预约"},
        {"name": "广州医科大学附属第一医院", "type": "public", "distance": "3.1km", "price": 26, "rating": 4.7, "department": "检验科", "wait_time": "40分钟", "booking_status": "可预约"},
        {"name": "美年大健康体检中心", "type": "private", "distance": "800m", "price": 45, "rating": 4.5, "department": "体检中心", "wait_time": "即约即检", "booking_status": "可预约"}
    ],
    "胸部CT": [
        {"name": "中山大学孙逸仙纪念医院", "type": "public", "distance": "1.2km", "price": 320, "rating": 4.9, "department": "影像科", "wait_time": "2-3天", "booking_status": "可预约"},
        {"name": "广东省人民医院", "type": "public", "distance": "2.5km", "price": 350, "rating": 4.8, "department": "放射科", "wait_time": "3-5天", "booking_status": "预约已满"},
        {"name": "广州医科大学附属第一医院", "type": "public", "distance": "3.1km", "price": 310, "rating": 4.7, "department": "影像中心", "wait_time": "2-4天", "booking_status": "可预约"},
        {"name": "爱康国宾体检中心", "type": "private", "distance": "1.8km", "price": 580, "rating": 4.6, "department": "影像科", "wait_time": "当天可检", "booking_status": "可预约"}
    ],
    "心电图": [
        {"name": "中山大学孙逸仙纪念医院", "type": "public", "distance": "1.2km", "price": 30, "rating": 4.9, "department": "心电图室", "wait_time": "20分钟", "booking_status": "可预约"},
        {"name": "广东省人民医院", "type": "public", "distance": "2.5km", "price": 32, "rating": 4.8, "department": "功能检查科", "wait_time": "30分钟", "booking_status": "可预约"},
        {"name": "广州医科大学附属第一医院", "type": "public", "distance": "3.1km", "price": 28, "rating": 4.7, "department": "心电图室", "wait_time": "25分钟", "booking_status": "可预约"},
        {"name": "慈铭体检中心", "type": "private", "distance": "1.5km", "price": 50, "rating": 4.4, "department": "检查科", "wait_time": "即时检查", "booking_status": "可预约"}
    ],
    "核磁共振": [
        {"name": "中山大学孙逸仙纪念医院", "type": "public", "distance": "1.2km", "price": 880, "rating": 4.9, "department": "MR室", "wait_time": "5-7天", "booking_status": "可预约"},
        {"name": "广东省人民医院", "type": "public", "distance": "2.5km", "price": 920, "rating": 4.8, "department": "磁共振科", "wait_time": "7-10天", "booking_status": "预约已满"},
        {"name": "广州医科大学附属第一医院", "type": "public", "distance": "3.1km", "price": 850, "rating": 4.7, "department": "影像中心", "wait_time": "5-8天", "booking_status": "可预约"},
        {"name": "瑞慈体检中心", "type": "private", "distance": "2.2km", "price": 1580, "rating": 4.5, "department": "影像科", "wait_time": "1-2天", "booking_status": "可预约"}
    ],
    "腹部B超": [
        {"name": "中山大学孙逸仙纪念医院", "type": "public", "distance": "1.2km", "price": 120, "rating": 4.9, "department": "超声科", "wait_time": "1-2天", "booking_status": "可预约"},
        {"name": "广东省人民医院", "type": "public", "distance": "2.5km", "price": 130, "rating": 4.8, "department": "超声医学科", "wait_time": "2-3天", "booking_status": "可预约"},
        {"name": "广州医科大学附属第一医院", "type": "public", "distance": "3.1km", "price": 115, "rating": 4.7, "department": "超声科", "wait_time": "1-3天", "booking_status": "可预约"},
        {"name": "美年大健康体检中心", "type": "private", "distance": "800m", "price": 200, "rating": 4.5, "department": "超声科", "wait_time": "当天可检", "booking_status": "可预约"}
    ],
    "肝功能": [
        {"name": "中山大学孙逸仙纪念医院", "type": "public", "distance": "1.2km", "price": 80, "rating": 4.9, "department": "检验科", "wait_time": "1天出报告", "booking_status": "可预约"},
        {"name": "广东省人民医院", "type": "public", "distance": "2.5km", "price": 85, "rating": 4.8, "department": "检验科", "wait_time": "1天出报告", "booking_status": "可预约"},
        {"name": "广州医科大学附属第一医院", "type": "public", "distance": "3.1km", "price": 78, "rating": 4.7, "department": "检验科", "wait_time": "1天出报告", "booking_status": "可预约"},
        {"name": "爱康国宾体检中心", "type": "private", "distance": "1.8km", "price": 120, "rating": 4.6, "department": "检验科", "wait_time": "当天出报告", "booking_status": "可预约"}
    ]
}

# 检查项目关键词映射（用于识别AI建议的检查项目）
check_item_keywords = {
    "血常规": ["血常规", "血液检查", "血细胞"],
    "胸部CT": ["胸部CT", "胸部 CT", "胸CT", "CT胸部", "肺部CT"],
    "心电图": ["心电图", "ECG", "心电"],
    "核磁共振": ["核磁", "核磁共振", "MRI", "磁共振"],
    "腹部B超": ["腹部B超", "腹部超声", "B超", "彩超"],
    "肝功能": ["肝功能", "肝功", "转氨酶"]
}

@app.route('/')
def index():
    return redirect(url_for('input_user_info'))

@app.route('/input')
def input_user_info():
    return render_template('input.html')

@app.route('/submit_user_info', methods=['POST'])
def submit_user_info():
    gender = request.form.get('gender')
    age = int(request.form.get('age', 0))
    height = float(request.form.get('height', 0))
    weight = float(request.form.get('weight', 0))
    
    # 计算BMI
    bmi = weight / ((height / 100) ** 2) if height > 0 else 0
    
    # 确定年龄段
    age_group = "青少年"
    for group, info in age_groups.items():
        if info['min'] <= age <= info['max']:
            age_group = group
            break
    
    # 存储用户信息到会话
    session['user_info'] = {
        'gender': gender,
        'age': age,
        'height': height,
        'weight': weight,
        'bmi': round(bmi, 2),
        'age_group': age_group
    }
    
    return redirect(url_for('select_option'))

@app.route('/select_option')
def select_option():
    if 'user_info' not in session:
        return redirect(url_for('input_user_info'))
    return render_template('select_option.html')

@app.route('/package_selection')
def package_selection():
    if 'user_info' not in session:
        return redirect(url_for('input_user_info'))
    
    user_info = session['user_info']
    age_group = user_info['age_group']
    packages = recommended_packages.get(age_group, [])
    
    return render_template('package_selection.html', 
                         user_info=user_info,
                         age_group=age_group,
                         packages=packages,
                         basic_diseases=basic_diseases,
                         bad_habits=bad_habits)

@app.route('/analyze_report')
def analyze_report():
    if 'user_info' not in session:
        return redirect(url_for('input_user_info'))
    
    user_info = session['user_info']
    return render_template('analyze_report.html', user_info=user_info)

@app.route('/submit_health_assessment', methods=['POST'])
def submit_health_assessment():
    if 'user_info' not in session:
        return redirect(url_for('input_user_info'))
    
    # 获取用户提交的健康评估信息
    diseases = request.form.getlist('diseases')
    habits = request.form.getlist('habits')
    other_info = request.form.get('other_info', '')
    
    # 存储健康评估信息到会话
    session['health_assessment'] = {
        'diseases': diseases,
        'habits': habits,
        'other_info': other_info
    }
    
    # 获取用户基本信息
    user_info = session['user_info']
    age_group = user_info['age_group']
    
    # 获取基础套餐
    base_packages = recommended_packages.get(age_group, [])
    
    # 根据健康状况调整套餐
    customized_packages = []
    for package in base_packages:
        # 创建套餐副本
        customized_package = package.copy()
        customized_package['items'] = package['items'].copy()
        
        # 根据基础疾病添加额外项目
        if '糖尿病' in diseases:
            if '血糖' not in customized_package['items']:
                customized_package['items'].append('血糖')
            if '糖化血红蛋白' not in customized_package['items']:
                customized_package['items'].append('糖化血红蛋白')
        
        if '高血压' in diseases:
            if '血压' not in customized_package['items']:
                customized_package['items'].append('血压')
            if '心电图' not in customized_package['items']:
                customized_package['items'].append('心电图')
        
        # 根据不良嗜好添加额外项目
        if '熬夜' in habits:
            if '肝功能' not in customized_package['items']:
                customized_package['items'].append('肝功能')
            if '肾功能' not in customized_package['items']:
                customized_package['items'].append('肾功能')
        
        if '吸烟' in habits:
            if '胸部CT' not in customized_package['items']:
                customized_package['items'].append('胸部CT')
        
        if '喝酒' in habits:
            if '肝功能' not in customized_package['items']:
                customized_package['items'].append('肝功能')
            if '血脂' not in customized_package['items']:
                customized_package['items'].append('血脂')
        
        # 更新套餐名称和描述
        if diseases or habits:
            customized_package['name'] = f"{package['name']}（定制版）"
            customized_package['description'] = f"{package['description']} - 根据您的健康状况定制"
        
        customized_packages.append(customized_package)
    
    return render_template('customized_package.html', 
                         user_info=user_info,
                         age_group=age_group,
                         diseases=diseases,
                         habits=habits,
                         customized_packages=customized_packages)

@app.route('/upload_report', methods=['POST'])
def upload_report():
    if 'user_info' not in session:
        return redirect(url_for('input_user_info'))
    
    # 获取上传的文件
    file = request.files.get('report_file')
    report_date = request.form.get('report_date', '')
    hospital = request.form.get('hospital', '')
    report_notes = request.form.get('report_notes', '')
    
    # 验证文件
    if not file:
        # 如果没有文件，重定向回上传页面并显示错误信息
        return redirect(url_for('analyze_report'))
    
    # 验证文件大小（10MB）
    max_size = 10 * 1024 * 1024
    if file.content_length > max_size:
        # 文件太大，重定向回上传页面
        return redirect(url_for('analyze_report'))
    
    # 验证文件类型
    allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
    import os
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        # 文件类型不允许，重定向回上传页面
        return redirect(url_for('analyze_report'))
    
    # 存储报告信息到会话
    session['report_info'] = {
        'filename': file.filename if file else '',
        'report_date': report_date,
        'hospital': hospital,
        'report_notes': report_notes
    }
    
    # 获取用户基本信息
    user_info = session['user_info']
    
    # 这里可以添加文件处理逻辑，如保存文件、分析报告等
    # 目前我们只是模拟分析结果
    
    # 模拟报告分析结果
    analysis_result = {
        'summary': '您的体检报告显示整体健康状况良好，但有一些需要注意的指标。',
        'abnormal_items': [
            {'name': '血糖', 'value': '6.2 mmol/L', 'reference': '3.9-6.1 mmol/L', 'advice': '建议控制饮食，增加运动，定期复查。'},
            {'name': '肝功能', 'value': 'ALT 45 U/L', 'reference': '0-40 U/L', 'advice': '建议减少熬夜，避免饮酒，保持良好的作息习惯。'}
        ],
        'recommendations': [
            '保持健康的饮食习惯，减少高糖、高脂肪食物的摄入。',
            '每周至少进行150分钟中等强度的有氧运动。',
            '保证充足的睡眠时间，避免熬夜。',
            '定期进行体检，监测健康状况。'
        ]
    }
    
    return render_template('report_analysis.html', 
                         user_info=user_info,
                         report_info=session['report_info'],
                         analysis_result=analysis_result)

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query', '').lower()
    results = []
    
    for category_id, items in sample_data.items():
        for item in items:
            if query in item['name'].lower() or query in item['description'].lower():
                item['category'] = next(cat['name'] for cat in test_categories if cat['id'] == category_id)
                results.append(item)
    
    return render_template('search_results.html', query=query, results=results, categories=test_categories)

@app.route('/test-selection')
def test_selection():
    return render_template('test_selection.html', categories=test_categories, data=sample_data)

@app.route('/chat')
def chat():
    user_info = session.get('user_info', {})
    return render_template('chat.html', user_info=user_info)

@app.route('/body_explorer')
def body_explorer():
    return render_template('body_explorer.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    import requests
    
    data = request.get_json()
    user_message = data.get('message', '')
    image_base64 = data.get('image', None)
    
    # 阶跃星辰 API配置
    api_key = '7603qS82OGbNVinkQCEeNAk6wTCHWJof0vCGJ2u6fwVNHqQj1yGl3rpoQmjnzMVtP'
    url = 'https://api.stepfun.com/v1/chat/completions'
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    
    # 获取用户基本信息
    user_info = session.get('user_info', {})
    
    # 构建系统提示词，包含用户信息
    system_prompt = '''你是"小鹰"，中山大学孙逸仙纪念医院的专业导诊助手。你的任务是为用户提供病症分析、检查建议和就医推荐。

【格式约束 - 必须严格遵守】
1. 绝对禁止使用Markdown语法（不要用 # 标题、** 加粗、- 列表、> 引用等符号）
2. 小标题必须使用中文方括号【】包裹，如【1. 疑似疾病分析】
3. 列表项使用数字 1. 2. 3. 格式，每项另起一行
4. 段落之间空一行
5. 不要使用任何特殊符号（除了中文标点和数字）

【输出结构 - 必须包含以下三部分】
当用户咨询具体病症时，必须按以下结构回复：

【1. 疑似疾病分析】
列出3个可能的疾病及其可能性（用百分比表示），简要说明判断依据。
格式示例：
1. 冠心病（可能性40%）：胸闷气短是典型症状，需排查心血管问题
2. 呼吸系统疾病（可能性30%）：可能存在肺部或气道问题
3. 焦虑症（可能性20%）：精神因素也可能引起类似症状

【2. 建议检验项目与科室】
明确说明应该挂什么科室，需要做哪些检查（必须包含具体检查项目名称，如"胸部CT"、"心电图"、"血常规"等）。
格式示例：
建议挂号科室：心内科
建议检查项目：
1. 心电图 - 初步评估心脏功能
2. 胸部CT - 排查肺部及心脏结构异常
3. 血常规 - 检查是否存在感染或贫血

【3. 就医推荐】
优先推荐中山大学孙逸仙纪念医院，然后推荐2-3家其他医院。需说明推荐理由和预约方式。
格式示例：
优先推荐：中山大学孙逸仙纪念医院
推荐理由：心血管科是国家重点专科，诊疗水平全国领先
预约方式：可通过医院官方微信公众号或114平台预约

其他推荐医院：
1. 广东省人民医院 - 综合实力强，心内科经验丰富
2. 广州医科大学附属第一医院 - 呼吸内科为国家重点学科

【重要提醒】
如果用户只是打招呼或咨询一般健康问题（非具体病症），可以简短回复，不需要按上述三部分结构输出。
只有在用户描述具体症状（如疼痛、不适、异常检查结果等）时，才启用三部分结构化输出。'''
    
    if user_info:
        system_prompt += f"\n\n【用户基本信息】（请在分析时参考这些信息，不要再询问）"
        system_prompt += f"\n性别：{user_info.get('gender', '未知')}"
        system_prompt += f"\n年龄：{user_info.get('age', '未知')}岁"
        system_prompt += f"\n身高：{user_info.get('height', '未知')}cm"
        system_prompt += f"\n体重：{user_info.get('weight', '未知')}kg"
        system_prompt += f"\nBMI：{user_info.get('bmi', '未知')}"
        system_prompt += f"\n年龄段：{user_info.get('age_group', '未知')}"
    
    # 构建用户消息内容（支持图片）
    if image_base64:
        # 打印调试信息
        print(f"收到图片数据，长度: {len(image_base64)}, 前50字符: {image_base64[:50]}")
        
        # 使用step-1v-32k模型处理图片（阶跃星辰的视觉模型）
        user_content = [
            {
                'type': 'text',
                'text': user_message
            },
            {
                'type': 'image_url',
                'image_url': {
                    'url': image_base64
                }
            }
        ]
        model = 'step-1v-32k'
        print(f"使用模型: {model}")
    else:
        # 纯文本消息
        user_content = user_message
        model = 'step-1-8k'
    
    payload = {
        'model': model,
        'messages': [
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': user_content
            }
        ],
        'temperature': 0.7,
        'top_p': 0.9
    }
    
    try:
        print(f"发送请求到API，模型: {payload['model']}")
        response = requests.post(url, headers=headers, json=payload, timeout=600)
        response.raise_for_status()
        result = response.json()
        
        print(f"API响应成功")
        ai_response = result['choices'][0]['message']['content']
        return {'success': True, 'response': ai_response}
    
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        print(f"API请求失败: {error_msg}")
        if hasattr(e.response, 'text'):
            print(f"响应内容: {e.response.text}")
            error_msg += f" | 响应: {e.response.text}"
        return {'success': False, 'error': error_msg}, 500
    except Exception as e:
        error_msg = f'处理请求时出错: {str(e)}'
        print(error_msg)
        return {'success': False, 'error': error_msg}, 500

@app.route('/api/hospital_prices', methods=['POST'])
def get_hospital_prices():
    """获取医院价格数据"""
    data = request.get_json()
    check_item = data.get('checkItem', '')
    
    # 查找匹配的检查项目
    matched_item = None
    for item_name, keywords in check_item_keywords.items():
        for keyword in keywords:
            if keyword in check_item:
                matched_item = item_name
                break
        if matched_item:
            break
    
    # 返回对应的医院价格数据
    if matched_item and matched_item in hospital_prices:
        return {
            'success': True,
            'checkItem': matched_item,
            'hospitals': hospital_prices[matched_item]
        }
    else:
        return {'success': False, 'message': '未找到该检查项目的价格信息'}
@app.route('/api/upload', methods=['POST'])
def api_upload():
    print(request.files)
    if 'report_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['report_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save the uploaded file
    # filename = secure_filename(file.filename)
    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    
    return jsonify({'message': 'File uploaded successfully', 'filename': file.filename, 'success': True}), 200

if __name__ == '__main__':
    app.run(debug=True)