from django import forms
from .models import BookReview


from django import forms
from .models import BookReview


class BookReviewForm(forms.ModelForm):

    class Meta:
        model = BookReview

        fields = [
            "rating",
            "comment",
        ]

        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "class": "review-comment",
                    "placeholder": "نظر خود را درباره این کتاب بنویسید...",
                    "rows": 6,
                }
            ),
        }

    def clean_rating(self):
        rating = self.cleaned_data["rating"]

        if rating < 1 or rating > 5:
            raise forms.ValidationError(
                "امتیاز باید بین ۱ تا ۵ باشد."
            )

        return rating

    def clean_comment(self):
        comment = self.cleaned_data["comment"].strip()

        if len(comment) < 3:
            raise forms.ValidationError(
                "نظر باید حداقل ۳ کاراکتر باشد."
            )

        return comment