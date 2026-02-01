from flask import Flask, render_template, request
import json

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('index.html', categories=test_categories, data=sample_data)

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

if __name__ == '__main__':
    app.run(debug=True)