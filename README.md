> Reprise après une pause : [guide pas à pas et schéma](docs/reprendre-le-lab.md).
> Le test HTTPS public est optionnel ; le parcours normal utilise le tunnel local.

# API e-commerce LAB

Catalogue de trois produits et calcul de devis en euros, avec montants entiers
en centimes. Pas de paiement, de commande persistée ou de données personnelles.
Les prix du client sont ignorés ; les quantités sont contrôlées. Flask et
Gunicorn, dépendances transitives figées, base Python figée par digest.

Endpoints : `GET /healthz`, `GET /readyz`, `GET /api/products`, `POST /api/quotes`.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
gunicorn --bind 127.0.0.1:8081 app:app
curl -H 'Content-Type: application/json' http://localhost:8081/api/quotes \
  --data '{"items":[{"product_id":"keyboard","quantity":2},{"product_id":"mouse","quantity":1}]}'
```

Le total attendu est `12300` centimes EUR. Les quatre tests, le processus
Gunicorn en conteneur non privilégié/read-only et l'audit pip-audit 2.10.1
passent. L'image initiale est poussée dans ACR et tirée par AKS sans secret
de registre. Cette validation utilise un pod temporaire supprimé après test ;
l'API permanente Dev est maintenant déployée par Argo CD depuis Git (Synced/Healthy).

Image initiale :
`tmgitops237d8c7f.azurecr.io/ecommerce-api@sha256:aa74f68b8c4df48276696c95593b50b1080de8e5001c0d6849f04c31effa63b4`.

## CI préparée

Le workflow teste chaque PR. Sur main, il teste, audite, se connecte à Azure
via OIDC, construit, scanne avec Trivy, pousse l'image scannée puis ouvre une
PR GitOps **Dev seulement** avec son digest. Il ne possède aucun kubeconfig.
Les actions sont figées par SHA. Les tests et le build Azure sont actifs. La promotion GitOps reste désactivée.
Le scan Python local ne constitue pas un scan de toutes les bibliothèques OS.

Dépôt public : https://github.com/kixb0002/ecommerce-app.

Prérequis avant activation : identité
Azure dédiée avec fédération GitHub main et rôle AcrPush au seul ACR,
variables AZURE_CLIENT_ID/AZURE_TENANT_ID/AZURE_SUBSCRIPTION_ID ; GitHub App
installée sur `platform-gitops` avec Contents et Pull requests write,
variable GITOPS_APP_ID et secret GITOPS_APP_PRIVATE_KEY. Ne pas réutiliser
l'application SSO comme identité de CI. Aucun de ces droits CI n'est inventé.
Activer `ENABLE_AZURE_BUILD=true` après validation Azure ; activer séparément
`ENABLE_GITOPS_PR=true` après configuration de la GitHub App. Un lancement
manuel est disponible. Le job de promotion dépend du build réussi.
Configurer les protections de branche et les approbations avant usage réel.

Le service reste interne, sans authentification applicative ; utiliser des
données de démonstration. Il ne s'agit pas d'une boutique complète prête à
encaisser des paiements. La persistance, l'identité client, les taxes et le
stock nécessitent une conception et des tests dédiés.

## Correction des vulnérabilités runtime

La base Debian initiale présentait 49 résultats HIGH système et 5 HIGH Python
au premier scan complet. La base est maintenant Python officielle Alpine 3.13,
figée par digest, et pip est désinstallé après installation des dépendances.
Les dépendances applicatives restent figées. Alpine utilise musl : toute future
dépendance native doit être validée avec cette base.

Vérifié le 14 novembre 2026 : quatre tests dans l’image non privilégiée/read-only,
HTTP Gunicorn health/catalogue/devis, Trivy 0.76.2 local et CI : zéro résultat
HIGH/CRITICAL, sans exception ni ignore-unfixed. Le scan local de secrets ne
signale aucun secret. Ceci ne garantit pas l’absence de vulnérabilités futures.

CI réussie et image poussée :
https://github.com/kixb0002/ecommerce-app/actions/runs/43620292447

Digest corrigé :
`sha256:307be498ba119ad1e10f574618b3b0b5c45ce41865ee53868d02c6f30874dae3`.
Promotion Dev : https://github.com/kixb0002/platform-gitops/pull/1.
Les références Staging/Prod restent des promotions manuelles et doivent être
remplacées par un digest scanné avant activation de ces environnements.

L’identité CI, sa fédération main et AcrPush sont gérés par Terraform ; le plan
après application ne détecte aucune différence. La promotion CI automatique
reste désactivée en attendant une GitHub App dédiée à platform-gitops.
