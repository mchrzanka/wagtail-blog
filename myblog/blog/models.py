from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.search import index #This module provides the necessary components to index and search content in the CMS.

# Create your models here.
class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    # this new get_context() method is overriding this exact method that already exists as part of the parent class (Page).
    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron. 
        
        # Super() is a built-in function that provides a way to call a method from a parent class (Page)(also known as a superclass) within a subclass (BlogIndexPage).

        #The super() function is used here to ensure that the BlogIndexPage version of get_context doesn't completely replace the functionality of the parent class's get_context. It allows you to include the behavior from the parent class while adding additional functionality in the child class's get_context method.
        context = super().get_context(request)
        #live() is a QuerySet filter that filters out pages that are not yet published
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context

class BlogPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250)
    body = RichTextField(blank=True)

    def main_image(self):
        gallery_item = self.gallery_images.first() #get first item from a set of gallery_images associated with the current instance (self). This is possible because of the ParentalKey called gallery_images.
        if gallery_item:
            return gallery_item.image
        else:
            return None

    #allows the content specified to be searchable via a search bar
    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    #InlinePanel handles related information directly within a parent item's edit page. Here, you can edit,create, or delete images right on the BlogPage page. Another example would be a "Product" model and each product can have multiple "Features". You can use InlinePanel to manage all the features directly from the product's edit page. 
    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"), #
    ]


#Inheriting from Orderable adds a sort_order field to the model, to keep track of the ordering of images in the gallery.
class BlogPageGalleryImage(Orderable):
    #A ParentalKey works similarly to a ForeignKey, but also defines BlogPageGalleryImage as a “child” of the BlogPage model. It is commonly used in conjunction with the InlinePanel and StreamField to represent a one-to-many or many-to-many relationship.

    #'models.CASCADE' means that when a BlogPage is deleted, all the related page objects will also be deleted.

    #When you access the gallery_images attribute of a BlogPage instance, it will provide you with all the related Image instances associated with that specific BlogPage.
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')

    #image is a ForeignKey to Wagtail’s built-in Image model, where the images themselves are stored. This appears in the page editor as a pop-up interface for choosing an existing image or uploading a new one. This way, we allow an image to exist in multiple galleries - effectively, we’ve created a many-to-many relationship between pages and images.

    #Wagtail's built-in image model, where the images themselves are stored.
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]
