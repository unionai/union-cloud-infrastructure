#!/usr/bin/env bash

set -ex

REGION=us-central1
PROJECT_ID=jeev-gcp-test
PROJECT_NUMBER="$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')"
GSA="serviceAccount:opta-permissions-scrape@${PROJECT_ID}.iam.gserviceaccount.com"

create_or_update_custom_role() {
    local rolename="$1"
    if gcloud iam roles list --project=${PROJECT_ID} --format='value(name)' | grep -Fq "projects/${PROJECT_ID}/roles/${rolename}"; then
        gcloud iam roles update "$@"
    else
        gcloud iam roles create "$@"
    fi
}

# Clear existing IAM role bindings
gcloud projects get-iam-policy ${PROJECT_ID} \
    --flatten=bindings \
    --filter="(bindings.members=(${GSA}))" \
    --format='value(bindings.role)' | \
    xargs -I {} gcloud projects remove-iam-policy-binding ${PROJECT_ID} \
    --member=${GSA} --role={} --all

if [ "${USE_GRANULAR_ROLES}" == "true" ]; then
    create_or_update_custom_role UnionaiProjectEditor --project=${PROJECT_ID} --file=union-ai-project-editor-role.yaml
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
            --member=${GSA} \
            --role="projects/${PROJECT_ID}/roles/UnionaiProjectEditor"

    create_or_update_custom_role UnionaiResourceOwner --project=${PROJECT_ID} --file=union-ai-resource-owner-role.yaml
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
            --member=${GSA} \
            --role="projects/${PROJECT_ID}/roles/UnionaiResourceOwner" \
            --condition=title=OwnedResourcesOnly,expression="\
resource.name == \"projects/_/buckets/artifacts.${PROJECT_ID}.appspot.com\" || \
resource.name.startsWith(\"projects/_/buckets/opta\") || \
resource.name.startsWith(\"projects/${PROJECT_ID}/global/addresses/opta\") || \
resource.name.startsWith(\"projects/${PROJECT_ID}/global/firewalls/opta\") || \
resource.name.startsWith(\"projects/${PROJECT_ID}/global/networks/opta\") || \
resource.name.startsWith(\"projects/${PROJECT_ID}/global/routes/default-route-\") || \
resource.name.startsWith(\"projects/${PROJECT_ID}/global/routes/opta\") || \
resource.name.startsWith(\"projects/${PROJECT_ID}/locations/${REGION}/keyRings/opta\") || \
resource.name.startsWith(\"projects/${PROJECT_ID}/regions/${REGION}/addresses/opta\") || \
resource.name.startsWith(\"projects/${PROJECT_ID}/regions/${REGION}/routers/opta\") || \
resource.name.startsWith(\"projects/${PROJECT_ID}/regions/${REGION}/subnetworks/opta\") || \
resource.name.startsWith(\"projects/${PROJECT_NUMBER}/secrets/opta\")"

    create_or_update_custom_role UnionaiStorageObjectAdmin --project=${PROJECT_ID} --file=union-ai-storage-object-admin-role.yaml
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
            --member=${GSA} \
            --role="projects/${PROJECT_ID}/roles/UnionaiStorageObjectAdmin" \
            --condition=title=TFStateBucketOnly,expression='resource.name.startsWith("projects/_/buckets/opta-tf-state")'

else
    create_or_update_custom_role UnionaiAdministrator --project=${PROJECT_ID} --file=union-ai-admin-role.yaml
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
            --member=${GSA} \
            --role="projects/${PROJECT_ID}/roles/UnionaiAdministrator"
fi
