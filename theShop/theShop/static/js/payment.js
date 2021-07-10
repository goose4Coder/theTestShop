
console.log("Sanity check!");
// new
// Get Stripe publishable ke

fetch("/stripe_config/")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.public_key);
  });
  fetch("/create_checkout_session/", { method: "POST", headers: {
            'X-CSRFToken': csrftoken
        },
      })
        .then(function (response) {
          return response.json();
        })
        .then(function (session) {
          return stripe.redirectToCheckout({ sessionId: session.sessionId });
        })
        .then(function (result) {
          // If redirectToCheckout fails due to a browser or network
          // error, you should display the localized error message to your
          // customer using error.message.
          if (result.error) {
            alert(result.error.message);
          }
        })
        .catch(function (error) {
          console.error("Error:", error);
        });




