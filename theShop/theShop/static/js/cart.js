var updateBtns = window.document.querySelectorAll(".update-cart")

for (i = 0; i < updateBtns.length; i++) {
  updateBtns[i].addEventListener('click', function(event){
  console.log('ok');
  var productId = event.target.dataset.product;
  var action = event.target.dataset.action;
  console.log('productId:', productId, 'Action:', action);
  if (user == 'AnonymousUser'){
			console.log('User is not authenticated');
		}
    else{
      console.log(user);
      updateUserOrder(productId, action);
      addCookieItem(productId, action);
    }
    // location.reload()
  })
}

function updateUserOrder(productId, action){
	console.log('User is authenticated, sending data...')

		var url = '/update_item/'

		fetch(url, {
			method:'POST',
			headers:{
				'Content-Type':'application/json',
        'X-CSRFToken':csrftoken,
			},
			body:JSON.stringify({'productId':productId, 'action':action})
		})
		.then((response) => {
		   return response.json();
		})
		// .then((data) => {
		//     console.log('Data:', data)
		// });
}
function addCookieItem(productId, action){
	console.log('User is not authenticated')

	if (action == 'add'){
		if (cart[productId] == undefined){
		cart[productId] = {'quantity':1}

		}else{
			cart[productId]['quantity'] += 1
		}
	}

	if (action == 'remove'){
		cart[productId]['quantity'] -= 1

		if (cart[productId]['quantity'] <= 0){
			console.log('Item should be deleted')
			delete cart[productId];
		}
	}
	console.log('CART:', cart)
	document.cookie ='cart=' + JSON.stringify(cart) + ";domain=;path=/"

	// location.reload()
}
