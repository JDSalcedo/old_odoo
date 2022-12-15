odoo.define('pos_boleta.screens', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');
var Session = require('web.Session');

var QWeb = core.qweb;
var mixins = core.mixins;

var PaymentScreenWidget = screens.PaymentScreenWidget;

	PaymentScreenWidget.include({
		
		click_invoice: function(){
	        var order = this.pos.get_order();
	        //funcionalidad anterior
	        /*
	        order.set_to_invoice(!order.is_to_invoice());
	        if (order.is_to_invoice()) {
	            this.$('.js_invoice').addClass('highlight');
	            this.pos.config.final_journal_id = this.pos.config.invoice_journal_id;
	        } else {
	            this.$('.js_invoice').removeClass('highlight');
	            this.pos.config.final_journal_id = false;
	        }
	        */
	        /*
	          Si al hacer click en el boton este esta seleccionado
	        	-se le quita la seleccion
	        	-se quita el atributo para ser facturado
	        	-se le asigna 'false' a 'final_journal_id'
	        */
	        if(this.$('.js_invoice').hasClass('highlight')){
	        	order.set_to_invoice(false);
	        	this.$('.js_invoice').removeClass('highlight');
	            this.pos.config.final_journal_id = false;
	        }else{
	        	if(!order.is_to_invoice()){
	        		order.set_to_invoice(!order.is_to_invoice());
	        	}
	        	this.$('.js_invoice').addClass('highlight');
	        	this.$('.js_boleta').removeClass('highlight');
	            this.pos.config.final_journal_id = this.pos.config.invoice_journal_id;
	        }
	    },
		
		click_boleta: function(){
	        var order = this.pos.get_order();
	        /*
	        order.set_to_invoice(!order.is_to_invoice());
	        if (order.is_to_invoice()) {
	            this.$('.js_boleta').addClass('highlight');
	            this.pos.config.final_journal_id = this.pos.config.boleta_journal_id;
	        } else {
	            this.$('.js_boleta').removeClass('highlight');
	            this.pos.config.final_journal_id = false;
	        }
	        */
	        /*
	          Si al hacer click en el boton este esta seleccionado
	        	-se le quita la seleccion
	        	-se quita el atributo para ser facturado
	        	-se le asigna 'false' a 'final_journal_id'
	        */
	        if(this.$('.js_boleta').hasClass('highlight')){
	        	order.set_to_invoice(false);
	        	this.$('.js_boleta').removeClass('highlight');
	            this.pos.config.final_journal_id = false;
	        }else{
	        	/*
	        	  si el boton no estaba seleccionado
		        	-se evalua si hay necesidad de darle el atributo de ser facturado, puede 
		        	darse el caso que antes estuvo seleccionado el otro diario(y la propiedad
		        	para ser facturado ya esta colocada por el otro diario)
		        	-se seleecciona el boton
		        	-se le quita la seleccion al otro boton
		        	-se le asigana el el journal seleccionado a 'final_journal_id'
	        	*/
	        	if(!order.is_to_invoice()){
	        		order.set_to_invoice(!order.is_to_invoice());
	        	}
	        	this.$('.js_boleta').addClass('highlight');
	        	this.$('.js_invoice').removeClass('highlight');
	            this.pos.config.final_journal_id = this.pos.config.boleta_journal_id;
	        }
	    },
		
		renderElement: function() {
			var self = this;
	        this._super();

	        this.$('.js_boleta').click(function(){
	            self.click_boleta();
	        });
	    },
	    
	    finalize_validation: function() {
	        var self = this;
	        var order = this.pos.get_order();

	        if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) { 

	                this.pos.proxy.open_cashbox();
	        }

	        order.initialize_validation_date();

	        if (order.is_to_invoice()) {
	            var invoiced = this.pos.push_and_invoice_order(order);
	            this.invoicing = true;

	            invoiced.fail(function(error){
	                self.invoicing = false;
	                if (error.message === 'Missing Customer') {
	                    self.gui.show_popup('confirm',{
	                        'title': _t('Please select the Customer'),
	                        'body': _t('You need to select the customer before you can invoice an order.'),
	                        confirm: function(){
	                            self.gui.show_screen('clientlist');
	                        },
	                    });
	                } else if (error.code < 0) {        // XmlHttpRequest Errors
	                    self.gui.show_popup('error',{
	                        'title': _t('The order could not be sent'),
	                        'body': _t('Check your internet connection and try again.'),
	                    });
	                } else if (error.code === 200) {    // OpenERP Server Errors
	                    self.gui.show_popup('error-traceback',{
	                        'title': error.data.message || _t("Server Error"),
	                        'body': error.data.debug || _t('The server encountered an error while receiving your order.'),
	                    });
	                } else {                            // ???
	                    self.gui.show_popup('error',{
	                        'title': _t("Unknown Error"),
	                        'body':  _t("The order could not be sent to the server due to an unknown error"),
	                    });
	                }
	            });
	            invoiced.done(function(){
	                self.invoicing = false;
	                self.gui.show_screen('receipt');
	            });
	        } else {
	            this.pos.push_order(order);
	            this.gui.show_screen('receipt');
	        }

	    },
	    
	});
});