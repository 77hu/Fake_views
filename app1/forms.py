from django import forms

class ReviewForm(forms.Form):
    RATING_CHOICES=[
    (1,'非常差'),
    (2,'差'),
    (3,'一般'),
    (4,'好'),
    (5,'非常好')
    ]
    VERIFIED_CHOICES=[
        ('Y','已验证购买'),
        ('N','未验证购买')
    ]
    PRODUCT_CATEGORY=[
        ('Apparel',"服装"),
        ('Shoes','鞋子'),
    ]
    rating=forms.TypedChoiceField(
        label='评分',
        choices=RATING_CHOICES,
        coerce=int,
        widget=forms.RadioSelect(attrs={'class': 'rating-radio'}),
        initial=4)
    verified_purchase=forms.ChoiceField(
        label='是否验证购买',
        choices=VERIFIED_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-control'}),
    )
    product_category=forms.ChoiceField(
        label='产品类别',
        choices=PRODUCT_CATEGORY,
        widget=forms.RadioSelect(attrs={'class': 'form-control'}),
    )
    product_title=forms.CharField(
        label='产品标题',
        max_length=200,
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                'placeholder': '夏季上新碎花裙',
                'required': True
                }),
        )
    review_title=forms.CharField(
        label='评论标题',
        max_length=200,
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'placeholder': '好好看，拍照超搭',
                    'required': True}
        )
    )
    review_text=forms.CharField(
        label='评论内容',
        widget=forms.Textarea(
            attrs={'class': 'form-control',
                   'rows': '5',
                   'placeholder': '请详细描述您的使用体验...',
                   'maxlength': 1000,
                   'required': True
                   }
        )
    )
    def clean_product_title(self):
        """产品标题验证"""
        title = self.cleaned_data['product_title'].strip()
        if len(title) < 5:
            raise forms.ValidationError(
                "产品标题至少需要5个字符",
                code='min_length'
            )
        return title

