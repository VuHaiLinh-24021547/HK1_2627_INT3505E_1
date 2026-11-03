**Product Endpoint Test**
* List products with pagination
* ![01](img/product/get_pagination.png)
* Get product by id, fail
* ![02](img/product/get_id_fail.png)
* Post new product
* ![03](img/product/post.png)
* Post existed product
* ![04](img/product/post_dupe_sku.png)
* Patch product
* ![05](img/product/patch.png)
* Delete
* ![06](img/product/delete.png)
* Purchase product
* ![07](img/product/purchase_2_product.png)
* Purchase product, fail
* ![08](img/product/urchase_fail.png)

**Order Endpoint Test**
* Create order
* ![09](img/order/create_order.png)
* Product not found
* ![10](img/order/product_404.png)
* List orders
* ![11](img/order/list_order.png)
* Get order by id
* ![12](img/order/get_order_id.png)
* Get order by id, fail
* ![13](img/order/get_order_fail.png)
* Add product to existing order
* ![14](img/order/add_product.png)
* Delete order
* ![15](img/order/delete.png)

**Healthz and Ready Endpoint Test**
* Healthz
* ![16](img/healthz_ready/healthz.png)
* Ready
* ![17](img/healthz_ready/ready.png)

**Pytest**
* ![18](img/pytest/pytest.png)