from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField
from django.db import models
from modelcluster.fields import ParentalKey
#ParentalKey : comme un ForeignKey, mais pensé pour les contenus "enfants" d'une page
#(ici, les champs du formulaire appartiennent a une page Contact precise)
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.snippets.models import register_snippet


class FormField(AbstractFormField):
    # AbstractFormField fournit deja tout ce qu'il faut pour decrire UN champ
    # quelconque (label, type de champ, obligatoire ou non...). On ajoute juste
    # le lien vers la page Contact. Les vrais champs (Nom, Email, Message) ne sont
    # PAS ecrits ici : ils seront crees comme des donnees, depuis l'admin (etape 5).
    page = ParentalKey(
        "ContactPage",
        on_delete=models.CASCADE,   # si la page Contact est supprimee, ses champs le sont aussi
        related_name="form_fields",
    )

class ContactPage(AbstractEmailForm):
    # On remplace Page par AbstractEmailForm : ContactPage reste une page (AbstractEmailForm
    # herite de Page), mais une page qui sait aussi envoyer un email a chaque reponse.
    intro = RichTextField(blank=True)          # texte affiche au-dessus du formulaire
    thankyoutext = RichTextField(blank=True)  # message affiche apres l'envoi
    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        InlinePanel("form_fields", label="Champs du formulaire"),
        # InlinePanel : widget d'admin qui affiche la liste des FormField de cette page,
        # avec un bouton pour en ajouter, en retirer, ou changer leur ordre
        FieldPanel("thankyoutext"),
        FieldPanel("to_address"),    # l'email de Max, qui recevra chaque message
        FieldPanel("from_address"),  # l'adresse "expediteur" affichee sur l'email recu
        FieldPanel("subject"),       # le sujet de l'email envoye
    ]


@register_snippet          # <- ce décorateur, posé juste au-dessus de la classe, fait tout le travail :
class Cours(models.Model):  #    il dit à Wagtail "ce modèle doit apparaître dans l'admin, avec son propre formulaire"
    nom = models.CharField(max_length=100)             # le nom du cours, ex: "Cardio Boost"
    horaire = models.CharField(max_length=100, blank=True)   # ex: "Lundi et jeudi, 18h00" (texte libre, pas une vraie heure)
    niveau = models.CharField(max_length=100, blank=True)     # ex: "Niveau intermédiaire"
    description = models.TextField(blank=True)          # TextField plutôt que CharField : pas de limite de longueur, pour un paragraphe

    panels = [
        # Liste des champs visibles dans le formulaire d'admin de CE Snippet.
        # On écrit "panels" et non "content_panels" : un Snippet n'est pas une Page,
        # il n'a donc pas de titre de page, de slug, de bouton "publier"... juste ses propres champs.
        FieldPanel("nom"),
        FieldPanel("horaire"),
        FieldPanel("niveau"),
        FieldPanel("description"),
    ]

    def str(self):
        # Sans cette méthode, Wagtail afficherait "Cours object (1)" dans la liste de l'admin.
        # Avec elle, c'est le nom du cours qui s'affiche à la place, bien plus lisible.
        return self.nom


class CoursPage(Page):
    def get_context(self, request):
        context = super().get_context(request)
        context ["cours_list"] = Cours.objects.all()
        return context 

class CoachsIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro")
    ]

    subpage_type = ["pages.CoachProfilPage"]

    def get_context(self, request, ):
        context = super().get_context(request)
        context ["coachs"] = CoachProfilPage.objects.child_of(self).live()

        return context

class CoachProfilPage(Page):
    specialite = models.CharField(max_length=100, blank=True)
    nom = models.CharField(max_length=50)
    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    bio = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("specialite"),
        FieldPanel("nom"),
        FieldPanel("photo"),
        FieldPanel("bio"),
    ]

parent_page_type = ["page.CoachsIndexPage"]