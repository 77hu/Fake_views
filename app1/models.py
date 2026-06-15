from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ReviewAnalysis(models.Model):
    """存储分析记录的业务模型"""
    ANALYSIS_STATUS=[
        ('PENDING', '处理中'),
        ('COMPLETED', '已完成'),
        ('FAILED', '分析失败')
    ]
    PREDICTION_RESULT=[
        ('REAL','真实评论'),
        ('FAKE','虚假评论'),
    ]
    user=models.ForeignKey(User,on_delete= models.CASCADE,verbose_name='用户')
    rating=models.IntegerField(verbose_name='评分')
    verified_purchase=models.CharField(max_length=1,verbose_name='是否验证购买')
    product_category=models.CharField(max_length=50,verbose_name='产品类别')
    product_title=models.CharField(max_length=200,verbose_name='产品标题')
    review_title=models.CharField(max_length=200,verbose_name='评论标题')
    review_text=models.TextField(verbose_name='评论内容')
    prediction_result=models.CharField(
        max_length=4,
        choices=PREDICTION_RESULT,
        verbose_name='预测结果'
    )
    fake_probability=models.FloatField(verbose_name='虚假概率')
    real_probability=models.FloatField(verbose_name='真实概率')
    status=models.CharField(
        max_length=10,
        choices=ANALYSIS_STATUS,
        default='PENDING',
        verbose_name='状态'
    )
    created_at=models.DateTimeField(default=timezone.now,verbose_name='创建时间')
    class Meta:
        verbose_name='评论分析记录'
        verbose_name_plural=verbose_name
        ordering=['-created_at']
    def __str__(self):
        return f'分析#{self.id} - {self.get_prediction_result_display()} ({self.fake_probability:.1f}%)'
    def save(self,*args,**kwargs):
        """自动设置状态"""
        if self.status == 'PENDING' and self.prediction_result:
            self.status = 'COMPLETED'
        super().save(*args, **kwargs)



