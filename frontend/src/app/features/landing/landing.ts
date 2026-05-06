import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Accordion, AccordionPanel, AccordionHeader, AccordionContent } from 'primeng/accordion';
import { Panel } from 'primeng/panel';

@Component({
  selector: 'app-landing',
  imports: [RouterLink, Accordion, AccordionPanel, AccordionHeader, AccordionContent, Panel],
  templateUrl: './landing.html',
  styleUrl: './landing.scss',
})
export class Landing {
  steps = [
    {
      num: 1,
      icon: 'fas fa-file-upload',
      title: 'Importez vos données',
      desc: 'Chargez votre fichier clients CSV. AdSeason analyse automatiquement la structure et valide vos données.',
    },
    {
      num: 2,
      icon: 'fas fa-sliders-h',
      title: 'Configurez votre campagne',
      desc: 'Choisissez la saison cible, définissez votre budget global et sélectionnez vos canaux prioritaires.',
    },
    {
      num: 3,
      icon: 'fas fa-chart-pie',
      title: 'Recevez vos recommandations',
      desc: "L'IA segmente vos clients et génère un plan publicitaire complet par profil, avec budget et ROI estimé.",
    },
    {
      num: 4,
      icon: 'fas fa-file-export',
      title: 'Exportez et partagez',
      desc: 'Téléchargez vos recommandations en PDF ou Excel pour les partager avec vos équipes marketing.',
    },
  ];

  services = [
    {
      value: '0',
      titre: 'Segmentation automatique des clients',
      contenu: "AdSeason analyse vos données clients et les regroupe automatiquement en profils homogènes. Chaque segment reçoit une stratégie publicitaire adaptée à son comportement d'achat.",
    },
    {
      value: '1',
      titre: 'Recommandations par saison',
      contenu: "Printemps, été, automne, hiver — chaque saison a ses opportunités. AdSeason tient compte des tendances saisonnières pour vous proposer les offres les plus pertinentes au bon moment.",
    },
    {
      value: '2',
      titre: 'Optimisation budgétaire',
      contenu: 'Définissez votre enveloppe globale et AdSeason la répartit intelligemment entre vos segments selon leur potentiel de retour sur investissement.',
    },
    {
      value: '3',
      titre: 'Multi-canaux & ROI estimé',
      contenu: 'Réseaux sociaux, email, affichage, radio... Pour chaque segment, la plateforme identifie les canaux les plus efficaces et vous donne une estimation du ROI attendu.',
    },
  ];

  faqs = [
    {
      value: '0',
      q: 'Quels formats de fichiers sont acceptés ?',
      r: "AdSeason accepte les fichiers CSV. Votre fichier doit contenir au minimum les colonnes : identifiant client, montant total des achats, fréquence d'achat et catégorie de produit.",
    },
    {
      value: '1',
      q: 'Mes données sont-elles sécurisées ?',
      r: 'Oui. Vos données sont chiffrées en transit (HTTPS) et au repos. Elles ne sont jamais partagées avec des tiers et restent accessibles uniquement depuis votre compte.',
    },
    {
      value: '2',
      q: 'Combien de temps faut-il pour obtenir des recommandations ?',
      r: "En général moins d'une minute. Le traitement dépend du volume de votre fichier, mais reste très rapide même pour plusieurs dizaines de milliers de clients.",
    },
    {
      value: '3',
      q: 'Puis-je générer des recommandations pour plusieurs saisons ?',
      r: 'Oui, vous pouvez générer autant de recommandations que vous le souhaitez, pour chaque saison, sur le même dataset ou sur des datasets différents.',
    },
    {
      value: '4',
      q: 'Comment exporter mes résultats ?',
      r: 'Depuis la page Historique, chaque recommandation peut être exportée en PDF (rapport complet mis en forme) ou en Excel (données brutes par segment).',
    },
  ];
}
