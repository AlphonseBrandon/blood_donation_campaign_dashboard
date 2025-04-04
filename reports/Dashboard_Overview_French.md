# Rapport de la Campagne de Don de Sang

## Comment Lancer le Tableau de Bord

### Étapes pour Lancer le Tableau de Bord

1.  **Ouvrir un Éditeur de Code**
    Commencez par lancer Visual Studio Code (VS Code).

2.  **Cloner le Dépôt**
    Ouvrez le contrôle de source, et clonez le dépôt.

    Lorsque vous êtes invité à entrer le dépôt, entrez [https://github.com/AlphonseBrandon/blood_donation_campaign_dashboard](https://github.com/AlphonseBrandon/blood_donation_campaign_dashboard)

    Clonez le dépôt, et voilà !, vous avez le tableau de bord dans votre espace de travail.

    Naviguez dans le répertoire cloné :

    Ensuite, ouvrez le terminal, et en vous assurant que tous les packages requis ont été installés, exécutez

    ```bash
    streamlit run src/dashboard.py
    ```

    Accéder au Tableau de Bord

    Après avoir exécuté la commande, votre navigateur web par défaut devrait s'ouvrir automatiquement, affichant le tableau de bord. S'il ne s'ouvre pas, vous pouvez naviguer manuellement vers http://localhost:8501.

    Votre tableau de bord devrait ressembler à ceci :

    ![Tableau de Bord](..\reports\figures\dashboard_images\home.PNG)


## Aperçu du Tableau de Bord

Le Tableau de Bord de la Campagne de Don de Sang fournit une analyse complète des données de don de sang, permettant aux organisateurs de campagne de prendre des décisions éclairées. Le tableau de bord présente diverses visualisations qui mettent en évidence les données démographiques des donneurs, l'efficacité de la campagne, les taux de rétention et l'impact des conditions de santé sur l'éligibilité au don. Cela permet une approche basée sur les données pour améliorer la sensibilisation et améliorer l'efficacité globale des campagnes de don de sang.

Nous avons le résumé suivant de nos donneurs
![Résumé Total de la campagne](..\reports\figures\dashboard_images\summary_of_entire_campaign.PNG)

Nous pouvons voir que, sur les 1 846 donneurs, l'âge moyen était de 31 ans, et le niveau moyen d'hémoglobine de 13,9 g/dL, donnant un pourcentage de taux d'éligibilité de 85,1 %.
Ces résultats de résumé sont expliqués ci-dessous ;

## 1. Profilage des Donneurs

Examinons maintenant les profils de nos différents donneurs, afin d'avoir une meilleure compréhension des données démographiques des personnes aptes au don de sang.

### 1.1 Donneurs par Ville Géographique

Comprendre la répartition géographique des donneurs aide à identifier les zones clés pour les campagnes ciblées. Voici un résumé de la répartition des donneurs par emplacement géographique.

![Résumé du Graphique des Villes Géographiques](..\reports\figures\dashboard_images\summary_of_town_distribution.PNG)

Le graphique montre que Douala est le principal contributeur au nombre de donneurs, avec 97,4 % des dons totaux provenant de cette ville. Cela met en évidence une zone concentrée pour les campagnes potentielles, indiquant où les ressources pourraient être le mieux allouées pour un impact maximal.

Notre tableau de bord vous permet de basculer entre les villes et les quartiers, permettant aux organisateurs de campagne d'adapter les stratégies en fonction des données démographiques et des comportements des donneurs locaux. Nous allons maintenant examiner les détails de la campagne dans le quartier de Douala 3 par exemple.

![Donneurs par Douala 3](..\reports\figures\dashboard_images\douala.png)

**Résumé des résultats :** D'après les résultats ci-dessus, nous voyons que les donneurs les plus nombreux (34) de Douala 3 proviennent de Yassa.

### 1.2 Donneurs par Groupes d'Âge

Nous examinerons ensuite la répartition par âge de nos donneurs. L'âge est une mesure cruciale pour comprendre quelles données démographiques sont les plus engagées dans le don de sang. En identifiant les groupes d'âge qui contribuent le plus, des initiatives de sensibilisation ciblées peuvent être développées pour encourager les dons au sein d'un groupe d'âge particulier.

![Graphique des Donneurs par Groupes d'Âge](..\reports\figures\dashboard_images\donor_per_age.png)

**Résumé des résultats :** La majorité des donneurs se situent dans la tranche d'âge 26-35 ans, représentant 826 donneurs, ce qui indique une base solide pour les efforts de sensibilisation ciblant les jeunes actifs de la classe ouvrière.

### 1.3 Donneurs par Profession

Lorsque nous comprenons quelles professions sont les plus représentées parmi les donneurs, cela aidera à adapter les campagnes à des travailleurs spécifiques.

![Graphique des Donneurs par Profession](..\reports\figures\dashboard_images\donor_per_profession.png)

**Résumé des résultats :** Le contexte professionnel des donneurs révèle que les étudiants constituent le segment le plus important, représentant 276 des donneurs totaux. Cette information peut nous aider à organiser des collectes de dons dans les établissements d'enseignement.

### 1.4 Donneurs par Sexe

La dynamique des genres joue un rôle important dans les taux de don de sang.

![Graphique des Donneurs par Sexe](..\reports\figures\dashboard_images\donor_per_gender.png)

**Résumé des résultats :** La répartition par sexe montre une prédominance des donneurs masculins, qui représentent 1664 (90,1 %) du total. Les stratégies visant à accroître la participation des femmes pourraient être bénéfiques, en particulier en ciblant les messages qui résonnent auprès des femmes. La plupart des femmes sont souvent confuses en raison des restrictions liées aux règles, à l'allaitement, etc., ce qui limite également le nombre de donneuses.

En conclusion, nous pouvons dire que le groupe d'âge le plus idéal était celui des 26-35 ans, la catégorie IMC typique étant le surpoids, et le sexe prédominant étant masculin, avec une hémoglobine moyenne de 14,0 g/dL, de profession étant étudiants, pour le don comme indiqué ci-dessous.

![donneur_idéal](..\reports\figures\dashboard_images\ideal_donor.PNG)

## 2. Efficacité de la Campagne

### 2.1 Efficacité par Âge et Sexe

En évaluant l'efficacité des campagnes par groupe d'âge, nous identifions les groupes d'âge les plus réceptifs aux efforts de sensibilisation.

![Graphique de l'Efficacité par Âge](..\reports\figures\dashboard_images\campaign_effectiveness_by_age.png)

Efficacité de la campagne par Sexe

![Graphique de l'Efficacité par Sexe](..\reports\figures\dashboard_images\campaign_effectiveness_by_gender.png)

**Résumé des résultats :** L'analyse indique que le groupe d'âge 26-35 ans a le nombre de dons le plus élevé, avec 826 donneurs provenant de ce groupe d'âge, donnant un taux de réussite de 86,2 %, et le moins étant ceux de 56-65 ans. Cela suggère que plus on vieillit, plus on est susceptible d'être naturellement exposé à des maladies comme le diabète, l'arrêt cardiaque, etc., ce qui les rend inéligibles au don de sang. En ce qui concerne le sexe, les hommes montrent une campagne plus efficace avec 1664 donneurs, à un taux de réussite de 90,1 %.

### 2.2 Efficacité par Lieu

L'analyse géographique révèle les zones avec les taux de participation les plus élevés et les plus faibles. Ces informations sont essentielles pour l'allocation des ressources dans les campagnes futures. Le graphique ci-dessous indique l'efficacité de la campagne dans les différents lieux où la campagne a été menée.

![Graphique de l'Efficacité par Lieu](..\reports\figures\dashboard_images\campaign_effectiveness_by_location.png)

**Résumé des résultats :** L'analyse géographique révèle que Douala est le lieu le plus efficace pour les campagnes, Douala affichant la contribution la plus élevée, 952 (91,3 %) aux dons totaux. Environ 14 donneurs n'ont pas précisé leurs villes, et le pourcentage le plus faible de donneurs provient de RAS, 6 donneurs, avec un taux d'efficacité de campagne de zéro.

### 2.3 Efficacité par Profession

Lorsque nous examinons l'efficacité de la campagne par profession, nous obtenons les résultats suivants.

![Graphique de l'Efficacité par Profession](..\reports\figures\dashboard_images\campaign_effectiveness_by_profession.png)

**Résumé des résultats :** Les étudiants sont le groupe de donneurs le plus efficace, contribuant à 206 des dons totaux, donnant un taux d'efficacité de campagne de 100 %. Cela renforce la nécessité d'initiatives de sensibilisation axées sur les étudiants, telles que des partenariats avec des universités et des collèges pour plus de dons de sang. Étant donné qu'ils ont indiqué être sans emploi, les besoins ultérieurs en emploi peuvent être satisfaits par le biais de la campagne.

## 3. Rétention des Donneurs
Dans cette section, nous examinons la probabilité qu'un donneur revienne pour un autre don, en fonction de ses données démographiques.

### Résumé de la Rétention des Donneurs

Mesurer la rétention des donneurs est crucial pour comprendre le succès des campagnes dans le maintien de relations à long terme avec les donneurs. Les mesures de rétention fournissent des informations sur l'efficacité avec laquelle les campagnes engagent et réengagent les donneurs. D'après la figure ci-dessous, nous voyons que 1 060 donneurs étaient des nouveaux donneurs, tandis que 786 étaient des donneurs réguliers, donnant un taux de rétention de 42,6 %.

![Graphique du Résumé de la Rétention](..\reports\figures\dashboard_images\sumary_of_donor_retention.PNG)

**Donneurs Réguliers :** 786 (42,6 % des donneurs totaux)
**Nouveaux Donneurs :** 1 060 (57,4 % des donneurs totaux)
**Taux de Rétention Global :** 42,6 %

**Résumé des résultats :** Le taux de rétention de 42,6 % indique un niveau sain de donneurs réguliers, soulignant l'importance de maintenir l'engagement avec les nouveaux donneurs et de les convertir en contributeurs réguliers, et si éligible, ce taux a la possibilité d'augmenter.

### 3.1 Rétention par Groupe d'Âge

L'analyse des taux de rétention par groupe d'âge aide à identifier les groupes d'âge les plus susceptibles de revenir pour des dons futurs. Cela nous aidera à informer les stratégies ciblées pour améliorer l'engagement des donneurs dans ce groupe d'âge particulier.

![Graphique de la Rétention par Groupe d'Âge](..\reports\figures\dashboard_images\donor_retention_age.png)

**Résumé des résultats :** L'analyse montre que les groupes d'âge plus âgés (56-65 ans) ont un taux de rétention plus élevé de 60 %, ce qui suggère des stratégies d'engagement efficaces au sein de cette démographie. Cela indique que les initiatives visant les jeunes donneurs pourraient devoir être renforcées car même s'ils constituent le pourcentage le plus élevé de donneurs, leur taux de rétention est faible, ce qui signifie qu'ils changent souvent d'avis sur le don.

### 3.2 Rétention par Profession

Comprendre la rétention par profession donne un aperçu des groupes professionnels les plus susceptibles de revenir pour des dons supplémentaires. Étant donné que la majorité des donneurs étaient des étudiants, les professions se concentreront sur les employés, comme indiqué dans le graphique ci-dessous.

![Graphique de la Rétention par Profession](..\reports\figures\dashboard_images\donor_retention_by_profession.png)

**Résumé des résultats :** La figure ci-dessous montre notre rétention par profession. Nous pouvons voir que ceux qui travaillent dans le domaine médical, les responsables des ressources humaines, les hommes de Dieu, la sécurité, etc. ont un taux de rétention de 100 %. Les moins représentés étaient les commerçants, les employés de salon, etc., ce qui indique des domaines potentiels pour améliorer la sensibilisation parmi ces professions.

### 3.3 Rétention par Lieu

L'évaluation des taux de rétention dans différents lieux géographiques permet de mieux comprendre où les campagnes réussissent ou échouent.

![Graphique de la Rétention par Lieu](..\reports\figures\dashboard_images\donor_retention_location.png)

**Résumé des résultats :** Le graphique montre que Douala a le taux de rétention le plus élevé parmi les lieux, renforçant son importance dans les campagnes futures. Cela suggère que les stratégies fonctionnant à Douala devraient être analysées et éventuellement reproduites dans d'autres régions, à l'échelle mondiale, car un taux de réussite de 100 % a été constaté dans les lieux que les donneurs n'ont pas mentionnés.

## 4. Impact des Conditions de Santé

### Résumé des Conditions de Santé

Les conditions de santé sont le facteur essentiel qui rend un donneur qualifié ou non pour le don. L'analyse des conditions de santé qui entraînent le report des donneurs est essentielle pour comprendre les obstacles au don. La résolution de ces problèmes améliorera l'éligibilité globale des donneurs.

![Graphique du Résumé des Conditions de Santé](..\reports\figures\dashboard_images\summary_of_health_conditions_impact.PNG)

**Résumé des résultats :** L'aperçu révèle que les conditions malsaines ont entraîné un taux de report de 21 % chez les donneurs potentiels, les problèmes les plus courants étant les personnes souffrant d'arrêt cardiaque. Cela indique un besoin d'initiatives éducatives sur la santé et le bien-être, car notre rétention est élevée chez les participants âgés, mais ils sont peu nombreux et la plupart souffrent de maladies cardiaques.

### Résumé de l'Éligibilité Totale

Comprendre l'éligibilité des donneurs est crucial pour évaluer le bassin de donneurs potentiels. Outre les conditions de santé, d'autres facteurs rendent une personne inéligible au don. Le graphique ci-dessous indique les statistiques d'inéligibilité globales de nos donneurs.

![Graphique du Résumé de l'Éligibilité Totale](..\reports\figures\dashboard_images\eligibility_summary.PNG)

**Donneurs Totaux Éligibles :** 1 571 (85,1 % du total)
**Donneurs Totaux Inéligibles :** 275 (14,9 % du total)
**Taux d'Éligibilité Global :** 85,1 %

**Résumé des résultats :** La majorité des donneurs sont éligibles au don de sang, ce qui indique un bassin de donneurs généralement sain et suggère que les efforts de sensibilisation peuvent être axés sur l'éducation des donneurs inéligibles, afin de rendre le bassin complet à 100 %.

### 4.1 Éligibilité par Âge

La répartition des taux d'éligibilité par groupe d'âge aide à identifier les groupes d'âge les plus susceptibles de répondre aux critères de don.

![Graphique de l'Éligibilité par Âge](..\reports\figures\dashboard_images\eligibility_by_age.png)

**Résumé des résultats :** L'analyse montre que les groupes d'âge plus âgés, 56-65 ans, ont un taux d'éligibilité plus faible, ce qui suggère que les problèmes de santé deviennent plus fréquents avec l'âge. Cela indique un besoin d'interventions de santé ciblées pour les populations âgées. Le groupe d'âge le plus éligible était celui des 36-45 ans.

### 4.2 Éligibilité par IMC

L'examen de l'éligibilité en fonction des catégories d'IMC donne un aperçu de la façon dont les mesures de santé influencent l'éligibilité des donneurs. L'indice de masse corporelle d'une personne en dit long sur son mode de vie, ce qui peut aider à savoir comment cibler les campagnes en fonction d'un mode de vie particulier des personnes.

![Graphique de l'Éligibilité par IMC](..\reports\figures\dashboard_images\eligibility_by_BMI.png)

**Résumé des résultats :** La figure indique que les personnes de la catégorie IMC "Normal" ont les taux d'éligibilité les plus élevés, tandis que celles classées comme "Obèses" montrent une éligibilité significativement plus faible, et il n'y avait personne qui était sévèrement obèse. Cela ne fait que renforcer l'importance de promouvoir des modes de vie sains parmi les donneurs potentiels.

## Données Brutes et Menu de Navigation

Le tableau de bord fournit également un accès aux données brutes pour une analyse plus approfondie et une compréhension de nos résultats.

![données_brutes](..\reports\figures\dashboard_images\raw_data.PNG)

## Barre de menu
Un menu de navigation permet aux utilisateurs de tester leur éligibilité en fonction des mesures fournies, ce qui rend notre tableau de bord flexible et interactif. Ceci afin d'améliorer l'expérience utilisateur et de faciliter l'utilisation de notre tableau de bord dans différents scénarios.

![vérifier_éligibilité](..\reports\figures\dashboard_images\check_eligibility.PNG)

Ce qui vous amène à l'API pour la vérification de l'éligibilité. 

Check your eligibility using the link: [check_eligibility](../https://testsiteg.pythonanywhere.com/)