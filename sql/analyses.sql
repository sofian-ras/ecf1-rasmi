-- ============================================
-- requetes analytiques pour datapulse
-- ============================================

-- requete 1: agregation simple
-- nombre de livres par categorie et prix moyen
select 
    categorie,
    count(*) as nombre_livres,
    round(avg(prix_eur), 2) as prix_moyen_eur,
    round(min(prix_eur), 2) as prix_min_eur,
    round(max(prix_eur), 2) as prix_max_eur
from livres
group by categorie
order by nombre_livres desc;

-- requete 2: jointure
-- librairies avec leur specialite et leur ville
-- croiser avec les livres pour voir les categories populaires par ville
select 
    l.ville,
    l.specialite,
    count(distinct l.nom_librairie) as nombre_librairies,
    liv.categorie,
    count(liv.id) as nombre_livres_categorie
from librairies l
cross join livres liv
where l.specialite is not null
group by l.ville, l.specialite, liv.categorie
order by l.ville, nombre_livres_categorie desc;

-- requete 3: fonction de fenetrage (window function)
-- classement des livres par prix dans chaque categorie
select 
    titre,
    categorie,
    prix_eur,
    note,
    row_number() over (partition by categorie order by prix_eur desc) as rang_prix,
    round(avg(prix_eur) over (partition by categorie), 2) as prix_moyen_categorie,
    prix_eur - round(avg(prix_eur) over (partition by categorie), 2) as ecart_moyenne
from livres
order by categorie, rang_prix;

-- requete 4: classement top n
-- top 10 des livres les plus chers avec bonne note
select 
    titre,
    categorie,
    prix_eur,
    note,
    disponibilite
from livres
where note >= 4
order by prix_eur desc
limit 10;

-- requete 5: analyse croisee entre sources
-- correlation entre specialite des librairies et categories de livres populaires
-- on croise les librairies avec les citations des auteurs
select 
    l.ville,
    l.nom_librairie,
    l.specialite,
    count(distinct c.auteur) as nombre_auteurs_citations,
    count(distinct liv.categorie) as nombre_categories_livres,
    round(avg(liv.prix_eur), 2) as prix_moyen_livres
from librairies l
cross join citations c
cross join livres liv
where l.ville is not null
group by l.ville, l.nom_librairie, l.specialite
having count(distinct c.auteur) > 0
order by l.ville, nombre_auteurs_citations desc;

-- ============================================
-- requetes bonus pour analyses supplementaires
-- ============================================

-- analyse des citations par auteur
select 
    auteur,
    count(*) as nombre_citations,
    array_agg(distinct unnest(tags)) as tous_les_tags
from citations
group by auteur
order by nombre_citations desc;

-- distribution des notes des livres
select 
    note,
    count(*) as nombre_livres,
    round(count(*) * 100.0 / sum(count(*)) over (), 2) as pourcentage
from livres
group by note
order by note desc;

-- librairies par ville avec coordonnees
select 
    ville,
    count(*) as nombre_librairies,
    round(avg(latitude), 4) as latitude_moyenne,
    round(avg(longitude), 4) as longitude_moyenne,
    array_agg(specialite) as specialites
from librairies
where latitude != 0 and longitude != 0
group by ville
order by nombre_librairies desc;

-- livres disponibles vs non disponibles par categorie
select 
    categorie,
    sum(case when disponibilite = 'In stock' then 1 else 0 end) as en_stock,
    sum(case when disponibilite != 'In stock' then 1 else 0 end) as rupture,
    count(*) as total
from livres
group by categorie
order by total desc;