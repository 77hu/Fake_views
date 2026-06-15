from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login,logout
from django.conf import settings
from django.utils import timezone
from .forms import ReviewForm
from .models import ReviewAnalysis
import numpy as np
import json
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import sys
import joblib
from django.shortcuts import render
from django.utils import timezone
import nltk

import seaborn as sns
from nltk.sentiment import SentimentIntensityAnalyzer

# 下载必要的 NLTK 数据（首次运行）
# nltk.download('punkt', quiet=True)
# nltk.download('stopwords', quiet=True)
# nltk.download('wordnet', quiet=True)
# nltk.download('omw-1.4', quiet=True)

#注册
def register(request):
    if request.method=='POST':
        form=UserCreationForm(request.POST)
        # print(form.is_valid())
        if form.is_valid():
            user=form.save()
            login(request,user)
            messages.success(request,"注册成功！")
            return redirect('login')
    else:
        form=UserCreationForm()
    return render(request,'register.html',{'form':form})


@login_required
def center(request):
    return render(request, 'history.html')

# views.py


# ========== 定义与训练时完全一致的函数 ==========
def combine_text_columns(X_df):
    combined = (
        X_df['PRODUCT_TITLE'].astype(str).fillna('__empty__') + " " +
        X_df['REVIEW_TITLE'].astype(str).fillna('__empty__') + " " +
        X_df['REVIEW_TEXT'].astype(str).fillna('__empty__')
    )
    return combined.replace(r'^\s*$', '__empty__', regex=True)

def preProcess(text):
    if pd.isna(text) or str(text).strip() == '':
        return ['__empty__']
    
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    import string

    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    table = str.maketrans('', '', string.punctuation)

    try:
        tokens = word_tokenize(str(text).lower())
        tokens = [word.translate(table) for word in tokens]
        tokens = [w for w in tokens if w.isalpha() and len(w) > 1]
        filtered = [w for w in tokens if w not in stop_words]
        if len(filtered) == 0 and len(tokens) > 0:
            filtered = tokens
        lemmatized = [lemmatizer.lemmatize(w) for w in filtered]
        bigrams = [' '.join(b) for b in nltk.bigrams(lemmatized)] if len(lemmatized) >= 2 else []
        result = lemmatized + bigrams
        return result if len(result) > 0 else ['__empty__']
    except Exception as e:
        print(f"Error in preProcess: {e}")
        return ['__error__']

# ========== 注入函数到 __main__ 模块 ==========
def inject_functions_to_main():
    main_module = sys.modules.get('__main__')
    if main_module is None:
        import types
        main_module = types.ModuleType('__main__')
        sys.modules['__main__'] = main_module

    if not hasattr(main_module, 'combine_text_columns'):
        setattr(main_module, 'combine_text_columns', combine_text_columns)
    if not hasattr(main_module, 'preProcess'):
        setattr(main_module, 'preProcess', preProcess)

# 执行注入
inject_functions_to_main()

# ========== 加载模型 ==========
model_path = r"E:\fake_review_rf_model.pkl"
try:
    loaded_model = joblib.load(model_path)
    print("✅ 模型加载成功")
except Exception as e:
    print(f"❌ 模型加载失败: {e}")
    loaded_model = None

@login_required
def home(request):
    if loaded_model is None:
        messages.error(request, "模型加载失败，无法进行分析。")
        return render(request, 'home.html', {'error_message': "模型加载失败"})

    form = ReviewForm()
    analysis_result = None
    error_message = None
    recent_analysis = ReviewAnalysis.objects.filter(user=request.user).order_by('-created_at')[:5]

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                rating = form.cleaned_data['rating']
                verified_purchase = form.cleaned_data['verified_purchase']
                product_category = form.cleaned_data['product_category']
                product_title = form.cleaned_data['product_title']
                review_title = form.cleaned_data['review_title']
                review_text = form.cleaned_data['review_text']

                new_data = pd.DataFrame({
                    'RATING': [int(rating)],
                    'VERIFIED_PURCHASE': [verified_purchase],
                    'PRODUCT_CATEGORY': [product_category],
                    'PRODUCT_TITLE': [product_title],
                    'REVIEW_TITLE': [review_title],
                    'REVIEW_TEXT': [review_text]
                })
                print(new_data.iloc[:,:4])
                
                prediction = loaded_model.predict(new_data)[0]
                probabilities = loaded_model.predict_proba(new_data)[0]
                print(prediction )
                # 假设 classes_ 是 ['fake', 'real'] 或 ['real', 'fake']
                fake_prob = probabilities[0] if loaded_model.classes_[0] == 'fake' else probabilities[1]
                real_prob = probabilities[1] if loaded_model.classes_[1] == 'real' else probabilities[0]

                analysis = ReviewAnalysis.objects.create(
                    user=request.user,
                    rating=rating,
                    verified_purchase=verified_purchase,
                    product_category=product_category,
                    product_title=product_title,
                    review_title=review_title,
                    review_text=review_text,
                    prediction_result='FAKE' if prediction == 'fake' else 'REAL',
                    fake_probability=fake_prob * 100,
                    real_probability=real_prob * 100
                )

                analysis_result = {
                    'id': analysis.id,
                    'prediction': '虚假评论' if prediction == 'fake' else '真实评论',
                    'fake_prob': round(fake_prob * 100, 2),
                    'real_prob': round(real_prob * 100, 2),
                    'timestamp': timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")
                }

                messages.success(request, "评论分析完成！")

            except Exception as e:
                error_message = f"分析失败: {str(e)}"
                messages.error(request, error_message)

    context = {
        'form': form,
        'analysis_result': analysis_result,
        'error_message': error_message,
        'recent_analysis': recent_analysis,
        'status': {
            'total_analyses': ReviewAnalysis.objects.filter(user=request.user).count(),
            'fake_ratio': ReviewAnalysis.objects.filter(user=request.user, prediction_result='FAKE').count() / max(1, ReviewAnalysis.objects.filter(user=request.user).count()) * 100
        }
    }

    return render(request, 'home.html', context)


@login_required
def analysis_detail(request, analysis_id=None):
    analysis = get_object_or_404(ReviewAnalysis, id=analysis_id, user=request.user)
    context = {
        'analysis': analysis,
    }
    return render(request, 'analysis_detail.html', context)

@login_required
def user_dashboard(request):
    """用户仪表盘 - 显示关键指标和最近活动"""
    # 获取用户统计信息
    total_analyses = ReviewAnalysis.objects.filter(user=request.user).count()
    fake_count = ReviewAnalysis.objects.filter(user=request.user, prediction_result='FAKE').count()
    fake_ratio = (fake_count / total_analyses * 100) if total_analyses > 0 else 0

    # ✅ 计算真实评论比例
    real_ratio = 100 - fake_ratio

    # 获取最近的5条分析记录
    recent_analyses = ReviewAnalysis.objects.filter(user=request.user).order_by('-created_at')[:5]

    # 获取最近的假评论
    recent_fake = ReviewAnalysis.objects.filter(user=request.user, prediction_result='FAKE').order_by('-created_at')[:3]

    context = {
        'total_analyses': total_analyses,
        'fake_ratio': fake_ratio,
        'real_ratio': real_ratio,  # ✅ 传入模板
        'recent_analyses': recent_analyses,
        'recent_fake': recent_fake,
        'stats': {
            'total_analyses': total_analyses,
            'fake_ratio': fake_ratio,
            'fake_count': fake_count,
            'real_count': total_analyses - fake_count
        }
    }

    return render(request, 'dashboard.html', context)

def net_graph(request):
    return render(request,'fake_review_dynamic.html')



def analyze_sentiment(text):
    """
    分析文本情感，返回VADER复合情感分数
    复合分数范围: [-1, 1]，越接近1越正面，越接近-1越负面
    """
    sia = SentimentIntensityAnalyzer()
    if pd.isna(text) or str(text).strip() == '':
        return 0  # 空文本视为中性

    # 获取复合情感分数
    sentiment = sia.polarity_scores(str(text))
    return sentiment['compound']

from django.shortcuts import render
import pandas as pd
from .models import ReviewAnalysis


@login_required
def heatmap_view(request):
    analyses = ReviewAnalysis.objects.filter(user=request.user).values(
        'rating', 'product_category', 'review_text'
    )
    df = pd.DataFrame(list(analyses))

    heatmap_data = None
    x_labels = []
    y_labels = []
    z_matrix = []

    if not df.empty and len(df) >= 2:
        df['sentiment_score'] = df['review_text'].apply(analyze_sentiment)

        try:
            # 创建透视表
            pivot = df.pivot_table(
                index='product_category',
                columns='rating',
                values='sentiment_score',
                aggfunc='mean'
            ).round(2)

            # 转为可序列化的格式
            z_matrix = pivot.values.tolist()
            x_labels = [str(col) for col in pivot.columns]
            y_labels = [str(idx) for idx in pivot.index]

            heatmap_data = {
                'z': z_matrix,
                'x': x_labels,
                'y': y_labels,
                'colorscale': [
                    [0, 'red'],      # -1: 负面
                    [0.5, 'white'],  # 0: 中性
                    [1, 'blue']      # +1: 正面
                ],
                'zmid': 0,  # 中心为0
                'type': 'heatmap',
                'text': [[f'情感分: {val:.2f}' for val in row] for row in z_matrix],  # 悬停文本
                'hoverinfo': 'text'
            }

        except Exception as e:
            print("热力图数据处理失败:", e)

    return render(request, 'heatmap.html', {
        'heatmap_data': json.dumps(heatmap_data) if heatmap_data else None,
        'has_data': not df.empty,
        'min_data': len(df) >= 2,
    })


from django.views.decorators.http import require_http_methods
from .models import ReviewAnalysis
from django.http import JsonResponse
@require_http_methods(["POST"])
@login_required
def delete_analysis(request, analysis_id):
    """删除用户的某条分析记录"""
    analysis = get_object_or_404(ReviewAnalysis, id=analysis_id, user=request.user)
    analysis.delete()
    return JsonResponse({'status': 'success'}, status=200)