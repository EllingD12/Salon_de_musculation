from wagtail.models import Page
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


class CoachPage(Page):
    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels +[
        FieldPanel("photo")
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
        context["cours_list"] = Cours.objects.all()
        return context 

class ContactPage(Page):
    pass