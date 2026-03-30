# Recipe Source Integration

## Supported sources

- `Anduin2017/HowToCook`
- `Gar-b-age/CookLikeHOC`

## Import policy

### HowToCook

Import only actual recipe directories under `dishes/`.

Exclude:
- condiments
- drinks
- desserts
- templates
- semi-finished helpers
- tips / starsystem / repo docs

### CookLikeHOC

Import only food category directories such as:
- `炒菜`
- `炖菜`
- `蒸菜`
- `砂锅菜`
- `凉拌`
- `汤`
- `早餐`
- `主食`

Do not import:
- docs
- images
- `配料`
- `饮品`
- build/theme infrastructure

## Merge policy

- keep both sources available at import time
- prefer `HowToCook` as the home-cooking default when duplicates are otherwise similar
- keep `CookLikeHOC` entries only when they still look like real home-executable dishes
- down-rank or exclude entries that depend on chain-style sauce bases, prepared soup bases, or industrialized workflow assumptions
