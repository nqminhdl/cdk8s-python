# cdk8s-python

## Import CRDs

```bash
cdk8s import imagepolicy:=crds/flux2_imagepolicy_crd.yaml --language python
cdk8s import imagerepository:=crds/flux2_imagerepository_crd.yaml --language python
```

## Run app

```bash
cdk8s synth
```
