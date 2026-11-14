# Livraison du LAB

1. Chaque PR et chaque push main exécute les tests et pip-audit.
2. Après autorisation et configuration de l’identité CI, ENABLE_AZURE_BUILD=true
   active la connexion OIDC sans secret Azure, le build, le scan Trivy et le push.
   Un scan HIGH/CRITICAL échoué bloque le push. Aucun accès AKS dans le workflow.
3. ENABLE_GITOPS_PR=true active séparément la proposition du digest Dev.
   Une GitHub App doit être installée uniquement sur platform-gitops, avec les
   permissions Contents: write et Pull requests: write. Configurer GITOPS_APP_ID
   et GITOPS_APP_PRIVATE_KEY dans ecommerce-app. Ne jamais publier sa clé privée.
4. Le propriétaire relit et fusionne la PR Dev ; Argo CD réconcilie ensuite Git.
   Vérifier Synced/Healthy puis les réponses healthz, catalogue et devis.
5. Staging et Prod restent des promotions manuelles ; aucun workflow ne les modifie.

En cas d’échec des tests/scans, corriger le code ou l’image avant relance.
En cas d’échec OIDC, vérifier le sujet exact et les variables Azure sans afficher
le token. En cas d’échec de promotion, le digest poussé reste dans ACR et Dev ne
change pas. Pour revenir en arrière, faire une PR restaurant un digest connu,
puis vérifier la réconciliation et la santé réelle.

Pour un dépôt nouvellement créé, le sujet inclut les IDs immuables GitHub :
https://docs.github.com/en/actions/reference/security/oidc#immutable-subject-claims

L’identité CI et la fédération sont déclarées dans platform-infra/environments/lab/ci.tf.
Le plan d’activation doit montrer seulement trois créations ; aucune application
Terraform n’a lieu automatiquement dans les workflows.
