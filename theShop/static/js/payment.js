console.log("Sanity check!");

// new
// Get Stripe publishable key
fetch("/stripe_config/")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.public_key);
   document.querySelector("#submitBtn").addEventListener("click", () => {
    // Get Checkout Session ID
    fetch("/create_checkout_session/").then((result) => {return result.json(); }).then((data) => {
      console.log(data);
      // Redirect to Stripe Checkout
    }).then((session)=>{
        return stripe.redirectToCheckout({sessionId: session.sessionId})
    }).then((res) => {
      console.log(res);
    });
  });
});

