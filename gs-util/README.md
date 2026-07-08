# Trackspace GSUtil (Google Cloud Storage Util)

Este repo sirve para:

1. Configurar CORS en los buckets de Firebase Storage — Seteás las reglas CORS tanto para dev (track-space-dev.firebasestorage.app) como para prod (track-space.firebasestorage.app) usando gsutil cors set.

2. Probar suscripciones de Google Play — Impersonás el service account y hacés requests a la API de Android Publisher para verificar que la configuración de permisos y la integración funcione correctamente.

## Build de imagen
```bash
docker build -t gsutil-python-3.11 .
```

## Ejecutar contenedor por primera vez
```bash
docker run -it gsutil-python-3.11
```

## Ejecutar contenedor existente
```bash
docker container start ID
docker exec -it ID bash
```

## Version de gsutil
```bash
gsutil --version
```

## Inicializar gcloud

USO nicoferella@gmail.com para setear el cors y el service account para probar las subscriptions

```bash
gcloud init
gcloud auth list
gcloud config set account 'ACCOUNT'

gcloud projects list
gcloud config set project 'PROJECT ID'
```

## Configurar cors

ACORDARSE DE COPIAR EL JSON ACTUALIZADO ADENTRO DEL CONTAINER (O HACER EL DOCKER BUILD DE NUEVO)

```bash
gsutil cors set cors-config-dev.json gs://track-space-dev.firebasestorage.app
gsutil cors get gs://track-space-dev.firebasestorage.app

gsutil cors set cors-config-prod.json gs://track-space.firebasestorage.app
gsutil cors get gs://track-space.firebasestorage.app
```

## Probar obtener una subscription con un service account desde comando

Esto mismo hace la cloud function para comprobar si la subscription es valida, pero de esta forma es mas facil probar si tenemos todo configurado ok:
* service account en cloud
* firebase integrations
* google play console permisos

```bash
gcloud auth print-access-token --impersonate-service-account=MAIL-DEL-SERVICE-ACCOUNT --scopes=https://www.googleapis.com/auth/androidpublisher
```

```bash
export ACCESS_TOKEN="ya29..."
```

```bash
curl -X GET "https://androidpublisher.googleapis.com/androidpublisher/v3/applications/com.trackspace.app/purchases/subscriptionsv2/tokens/PURCHASE-TOKEN-DE-SUBSCRIPCION" -H "Authorization: Bearer $ACCESS_TOKEN" -H "Accept: application/json"
```

```json
# EXAMPLE RESPONSE

{
    "kind": "androidpublisher#subscriptionPurchaseV2",
    "startTime": "2025-07-15T01:27:17.014Z",
    "regionCode": "AR",
    "subscriptionState": "SUBSCRIPTION_STATE_EXPIRED",
    "latestOrderId": "GPA.3366-0669-7676-46707..5",
    "canceledStateContext": {
    "systemInitiatedCancellation": {}
    },
    "testPurchase": {},
    "acknowledgementState": "ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED",
    "lineItems": [
    {
        "productId": "premium",
        "expiryTime": "2025-07-15T02:02:17.332Z",
        "autoRenewingPlan": {
        "recurringPrice": {
            "currencyCode": "USD",
            "units": "1",
            "nanos": 990000000
        }
        },
        "offerDetails": {
        "basePlanId": "basic"
        },
        "latestSuccessfulOrderId": "GPA.3366-0669-7676-46707..5"
    }
    ]
}
```