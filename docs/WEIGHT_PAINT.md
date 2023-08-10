# Weight Paint
These functions make it easier to weight paint clothing/hair/etc. to add realistic cloth/soft-body sims.

## Vertex Select by Weight
With active object, deselect all vertices (optional), then select only vertices with weights between 'Min Weight' and 'Max Weight', inclusive.
'Deselect all first' is enabled by default, if enabled then all mesh vertexes are deselected before Select by Weight operation is applied.

## Grow Selection Paint
Starting with currently selected vertexes (of active object), set weight paint in successive 'rings' by using 'select more' and weight painting only newly selected vertexes - blending weight paint value by 'select more' iteration. Very useful, e.g. on dresses, to weight paint 1.0 at waist and blend to 0.0 at edge of dress.
The Grow Selection Paint function creates a gradient from selected vertexes outward (using Blender's builtin 'Grow Selection' operation).
- e.g. top of a pair of pants would likely have weight = 1.0 for full strength pin, while the bottoms of the pant legs should have weight = 0.1 for minimal pinning. To use Grow Selection Paint in this case - select the top rows of pants' vertexes, estimate the number of "grow" operations to select the rest of the pants, and hit Grow Paint.

'Iterations' controls amount of growth, this is how many times 'Select More' is applied.

'Start Weight' is applied to currently selected vertexes, and used as beginning blend value.

'End Weight' is applied to vertexes in last 'Select More' iteration.

'Paint Initial Selection' (enabled by default)
  -enable so that initially selected vertexes will be painted with 'Start Weight'
  -disable so that only 'growth' vertexes will be painted

'Tail Fill' (disabled by default)
  -if enabled then 'Tail Value' is weight painted to any vertexes that remain unselected after 'Iterations' weight paint is applied
  - basically, an 'Invert Selection' operation is applied after all growth weight paint is applied

'Fill Only Linked' (enabled by default)
  -if enabled then 'Tail fill' is applied only to vertexes that are 'linked' - i.e. connected by edges
