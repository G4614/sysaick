# 医疗咨询AI智能推荐系统 - 功能演示

## 功能概述

当用户咨询具体病症时（如"胸闷气短"），系统自动完成两个动作：

### 动作A：结构化文本回复
AI助手"小鹰"会按照以下严格格式回复：

```
【1. 疑似疾病分析】
1. 冠心病（可能性40%）：胸闷气短是典型症状，需排查心血管问题
2. 呼吸系统疾病（可能性30%）：可能存在肺部或气道问题
3. 焦虑症（可能性20%）：精神因素也可能引起类似症状

【2. 建议检验项目与科室】
建议挂号科室：心内科
建议检查项目：
1. 心电图 - 初步评估心脏功能
2. 胸部CT - 排查肺部及心脏结构异常
3. 血常规 - 检查是否存在感染或贫血

【3. 就医推荐】
优先推荐：中山大学孙逸仙纪念医院
推荐理由：心血管科是国家重点专科，诊疗水平全国领先
预约方式：可通过医院官方微信公众号或114平台预约

其他推荐医院：
1. 广东省人民医院 - 综合实力强，心内科经验丰富
2. 广州医科大学附属第一医院 - 呼吸内科为国家重点学科
```

### 动作B：自动渲染价格对比卡片
系统会自动识别AI建议中的检查项目（如"胸部CT"、"心电图"、"血常规"），并在回复下方渲染价格对比卡片，包含：

- 🏥 中山大学孙逸仙纪念医院（优先推荐）
- 🏥 广东省人民医院
- 🏥 广州医科大学附属第一医院
- 🏥 第三方体检中心

每个医院卡片显示：
- 医院名称 + 类型标签（公立/私立）
- ⭐ 评分
- 💰 预估价格（醒目显示）
- 📍 距离
- 🏢 科室
- ⏰ 等待时间
- 📅 预约按钮

## 技术实现

### 1. System Prompt 设计（UI.py）

```python
system_prompt = '''你是"小鹰"，中山大学孙逸仙纪念医院的专业导诊助手。

【格式约束 - 必须严格遵守】
1. 绝对禁止使用Markdown语法（不要用 # ** - 等符号）
2. 小标题必须使用中文方括号【】包裹
3. 列表项使用数字 1. 2. 3. 格式
4. 段落之间空一行

【输出结构 - 必须包含以下三部分】
当用户咨询具体病症时：
1.【1. 疑似疾病分析】- 列出3个可能性及百分比
2.【2. 建议检验项目与科室】- 明确挂号科室和具体检查项目
3.【3. 就医推荐】- 优先推荐中山大学孙逸仙纪念医院
'''
```

### 2. 医院价格数据（Mock Data）

```python
hospital_prices = {
    "胸部CT": [
        {
            "name": "中山大学孙逸仙纪念医院",
            "type": "public",
            "distance": "1.2km",
            "price": 320,
            "rating": 4.9,
            "department": "影像科",
            "wait_time": "2-3天",
            "booking_status": "可预约"
        },
        # ... 更多医院数据
    ]
}
```

### 3. 检查项目识别（JavaScript）

```javascript
const CHECK_ITEM_KEYWORDS = {
    "血常规": ["血常规", "血液检查", "血细胞"],
    "胸部CT": ["胸部CT", "胸部 CT", "胸CT", "CT胸部", "肺部CT"],
    "心电图": ["心电图", "ECG", "心电"],
    "核磁共振": ["核磁", "核磁共振", "MRI", "磁共振"],
    "腹部B超": ["腹部B超", "腹部超声", "B超", "彩超"],
    "肝功能": ["肝功能", "肝功", "转氨酶"]
};

function detectCheckItems(aiResponse) {
    const detectedItems = [];
    for (const [itemName, keywords] of Object.entries(CHECK_ITEM_KEYWORDS)) {
        for (const keyword of keywords) {
            if (aiResponse.includes(keyword)) {
                if (!detectedItems.includes(itemName)) {
                    detectedItems.push(itemName);
                }
                break;
            }
        }
    }
    return detectedItems;
}
```

### 4. 价格卡片渲染函数

```javascript
async function renderPriceCard(checkItem, parentElement) {
    const response = await fetch('/api/hospital_prices', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ checkItem: checkItem })
    });
    
    const data = await response.json();
    
    if (data.success && data.hospitals) {
        // 创建卡片容器
        const cardContainer = document.createElement('div');
        cardContainer.className = 'price-card-container';
        
        // 渲染每家医院
        data.hospitals.forEach(hospital => {
            // ... 渲染医院卡片HTML
        });
        
        parentElement.appendChild(cardContainer);
    }
}
```

### 5. 自动触发逻辑

```javascript
function addMessageToDOM(type, content, imageUrl = null) {
    // ... 基础消息渲染
    
    // 如果是AI回复，自动检测并渲染价格卡片
    if (type === 'assistant') {
        const checkItems = detectCheckItems(content);
        if (checkItems.length > 0) {
            checkItems.forEach(item => {
                renderPriceCard(item, contentDiv);
            });
        }
    }
}
```

## 测试场景

### 场景1：胸闷气短
**用户输入：** "我最近胸闷气短，在广州海珠区"

**AI回复：** 
- 【1. 疑似疾病分析】→ 冠心病/呼吸系统疾病/焦虑症
- 【2. 建议检验项目与科室】→ 心内科 + 心电图、胸部CT、血常规
- 【3. 就医推荐】→ 中山大学孙逸仙纪念医院

**自动触发：**
- 识别到"心电图" → 渲染心电图价格卡片（4家医院）
- 识别到"胸部CT" → 渲染胸部CT价格卡片（4家医院）
- 识别到"血常规" → 渲染血常规价格卡片（4家医院）

### 场景2：腹痛不适
**用户选择：** 了解疾病 → 消化与排泄 → 勾选症状

**AI回复：**
- 【1. 疑似疾病分析】→ 胃炎/肠炎/胆囊炎
- 【2. 建议检验项目与科室】→ 消化内科 + 腹部B超、肝功能、血常规
- 【3. 就医推荐】→ 中山大学孙逸仙纪念医院

**自动触发：**
- 识别到"腹部B超" → 渲染价格卡片
- 识别到"肝功能" → 渲染价格卡片
- 识别到"血常规" → 渲染价格卡片

## 样式特点

### 价格卡片设计（"逸仙绿"风格）
- 背景色：#f8fdf9（浅绿背景）
- 边框：#d4f0e0（中大绿淡化）
- 主色调：#005826（中大绿）
- 价格字体：24px 粗体，醒目显示
- 悬停效果：卡片上浮 + 阴影加深
- 公立医院标签：绿色系
- 私立医院标签：橙色系

### 交互体验
- ✅ 可预约：绿色按钮，点击触发预约
- ❌ 预约已满：灰色禁用按钮
- 🔍 详情按钮：白底绿边，查看医院详细信息
- 💡 底部提示：价格仅供参考 + 优先推荐逸仙医院

## API端点

### POST /api/chat
处理用户消息，返回AI结构化回复

### POST /api/hospital_prices
```json
// 请求
{
    "checkItem": "胸部CT"
}

// 响应
{
    "success": true,
    "checkItem": "胸部CT",
    "hospitals": [
        {
            "name": "中山大学孙逸仙纪念医院",
            "type": "public",
            "distance": "1.2km",
            "price": 320,
            "rating": 4.9,
            "department": "影像科",
            "wait_time": "2-3天",
            "booking_status": "可预约"
        }
        // ... 更多医院
    ]
}
```

## 使用说明

1. 启动服务器：`python UI.py`
2. 访问：http://127.0.0.1:5000/chat
3. 输入症状或选择"了解疾病"填写表单
4. AI自动回复结构化内容
5. 价格卡片自动渲染在回复下方
6. 点击"立即预约"或"详情"查看更多信息

## 注意事项

- 只有在AI回复中包含具体检查项目关键词时才会触发价格卡片
- 如果用户只是打招呼或一般性咨询，不会触发结构化输出
- 价格数据为模拟数据，实际使用需对接真实医院API
- 预约和详情功能为占位符，需进一步开发

## 配色方案

- 主色调：#005826（SYSU中大绿）
- 悬停：#00722f
- 背景：#f8fdf9 / #f0f9f4
- 边框：#d4f0e0
- 文字：#333（主）/ #666（次）/ #999（辅）
- 强调：#ff9800（评分）
