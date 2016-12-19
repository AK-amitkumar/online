$(document).ready(function () {

    // Test if i can find the input field of the chkoutbox
    $('.oe_website_sale').each(function () {
        var oe_website_sale = this;

        // Update Sales Order by CheckoutBox Inputs for One-Page Checkout
        $(oe_website_sale).find("form input.js_quantity").on("change", function () {
            console.log('Checkoutbox input changed');

            // Store the input dom in a var
            var $input = $(this);
            // In case of already running update do nothing ;)
            if ($input.data('update_change')) {
                return;
            };

            // EXTRACT DATA FROM HTML
            // Product Quantity
            var value = parseInt($input.val(), 10);
            if (isNaN(value)) value = 0;
            console.log('Product Quantity (value): ' + value);
            // Product ID(s) (in fact it is only one ID)
            // HINT: The product.product is needed here!
            // HINT: product id MUST BE an INT and not a string or you will get strange access errors in odoo
            var product_id = parseInt($(oe_website_sale).find(".js_product input.product_id").val(), 10);
            console.log('Product Id (value): ' + product_id);
            var product_ids = [product_id];
            console.log('Product Ids (parseInt): ' + product_ids);
            // Get the sales order line ID
            var line_id = parseInt($input.data('line-id'),10);
            console.log('SaleOrderLine ID (parseInt): ' + line_id);
            if (isNaN(line_id)) line_id = false;

            // START UPDATE
            // Prevent concurrent Updates
            $input.data('update_change', true);

            // update_json (update the Sale order)
            openerp.jsonRpc("/shop/cart/update_json", 'call', {
                'line_id': line_id,
                'product_id': product_id,
                'set_qty': value})
                    .then(function (data) {
                        // Remove Concurrent-Update Lock
                        $input.data('update_change', false);
                        // Value may be 0 (Quantity) and parseInt($input.val(), 10) may return NAN
                        // I guess this means that if in the meantime the input was changed we
                        // start again?
                        if (value !== parseInt($input.val(), 10)) {
                            console.log('Quantity of input was changed while processing update!');
                            $input.trigger('change');
                            return;
                        }
                        // Reload page if the quantity of the sale_order_line is None (Error case)
                        if (!data.quantity) {
                            console.log('Returned Data of /shop/cart/update_json has no .quantity attrib');
                            location.reload(true);
                            return;
                        }
                        console.log('!data.quantity: ' + !data.quantity);
                        console.log('data.quantity: ' + data.quantity);

                        // var $q = $(".my_cart_quantity");
                        // $q.parent().parent().removeClass("hidden", !data.quantity);
                        // $q.html(data.cart_quantity).hide().fadeIn(600);
                        //
                        // $input.val(data.quantity);
                        // $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);
                        // $("#cart_total").replaceWith(data['website_sale.total']);
                    });

            //
        });
    });






    // Set Suggested Price by Buttons
    var $price_donate = $("#price_donate");
    var $price_suggested = $(".price_donate_suggested");
    $price_suggested.on("click", function (ev1) {
        $price_donate.val( $(this).data("price") );
    });

    // Click radio input of the selected payment interval on first load of the page
    $("input[name='payment_interval_id'][checked]").ready(function () {
        //console.log('On Load of Payment Intervalls');
        $("input[name='payment_interval_id'][checked]").trigger('click');
    });
    // Click select option of the selected payment interval on first load of the page
    $("select[name='payment_interval_id']").ready(function () {
        //console.log('On Load of Payment Intervalls Selection');
        $("select[name='payment_interval_id'] option:selected").trigger('change');
    });

    // Hide all tabs and related tab-content that are not recurring if recurring payment is selected
    var $radio_payint = $("input[name='payment_interval_id']");
    $radio_payint.on("click", function (ev) {
        if ( $(this).attr('data-payment-interval-external-id') != 'website_sale_donate.once_only' ) {

            // hide all acquirer tabs that do not work with recurring transactions if any
            $( "[data-recurring-transactions='False']").addClass('hidden');

            // Check if active tab is now hidden and if 'click' the next non hidden tab
            if ( !($('#payment_method li.active:not(.hidden)').length) ) {
                //console.log('No Tab Active');
                // Select next non hidden tabs (li) link (a) and click it
                $('#payment_method li:not(.hidden) a[role="tab"]:first').trigger('click');
            };

        } else {
            // Unhide all tabs and its content if no recurring payment interval is selected
            $( "[data-recurring-transactions='False']").removeClass('hidden');
        }
    });
    // Hide all tabs and related tab-content that are not recurring if recurring payment is selected
    var $select_payint = $("select[name='payment_interval_id']");
    $select_payint.on("change", function (ev) {
        var data_payment_interval_external_id = $( "select[name='payment_interval_id'] option:selected" ).attr('data-payment-interval-external-id');
        if ( data_payment_interval_external_id != 'website_sale_donate.once_only' ) {

            // hide all acquirer tabs that do not work with recurring transactions if any
            $( "[data-recurring-transactions='False']").addClass('hidden');

            // Check if active tab is now hidden and if 'click' the next non hidden tab
            if ( !($('#payment_method li.active:not(.hidden)').length) ) {
                //console.log('No Tab Active');
                // Select next non hidden tabs (li) link (a) and click it
                $('#payment_method li:not(.hidden) a[role="tab"]:first').trigger('click');
            };

        } else {
            // Unhide all tabs and its content if no recurring payment interval is selected
            $( "[data-recurring-transactions='False']").removeClass('hidden');
        }
    });

    // Select (check) radio input tag of the acquirer tab on tab click
    var $payment = $("#payment_method");
    $('#payment_method a[role="tab"]').on("click", function (e) {

        // Set tab-related hidden radio-input-tag to checked
        $('ul[role="tablist"]').find("input[name='acquirer']:checked").removeAttr('checked');
        $( this ).find("input[name='acquirer']").prop('checked', true);

        // Disable the other input tags (payment methods) (maybe not needed)
        var payment_id = $( this ).find("input[name='acquirer']").val();
        $("div.tab-content div[data-id] input", $payment).attr("disabled", "true");
        $("div.tab-content div[data-id='"+payment_id+"'] input", $payment).removeAttr("disabled");
    });

    // Make the stuff from website_sale website_sale_payment.js work with our acquirer tabs if not OPC
    // When clicking on payment button: create the tx using json then continue to the acquirer
    $payment.on("click", 'button[type="submit"],button[name="submit"]', function (ev) {
        console.log('Mike Acquirer Submit Button: preventDefault stopPropagation')
        ev.preventDefault();
        ev.stopPropagation();
        var $form = $(ev.currentTarget).parents('form');
        var acquirer_id = $(ev.currentTarget).parents('div.acquirer_button_not_opc').first().data('id');
        if (!acquirer_id) {
            console.log('Mike: No acquirer ID');
            return false;
        }
        openerp.jsonRpc('/shop/payment/transaction/' + acquirer_id, 'call', {}).then(function (data) {
            console.log('Mike: SUBMIT FORM');
            $form.submit();
        });
    });


    // Equal content height tab boxes
    var maxHeight=0;
    $(".tab-content.tab-equal-heights .tab-pane").each(function(){
        var height = $(this).height();
        maxHeight = height>maxHeight?height:maxHeight;
    });
    $(".tab-content.tab-equal-heights").height(maxHeight);

    // DISABLED: Update Page on Delivery-Method Change
    // HINT: Disabled because it is better to press the next button than the auto submit of the form
    //$("bla bla").find("input[name='delivery_type']").click(function (ev) {
    //    $(ev.currentTarget).parents('form').submit();
    //});
});


