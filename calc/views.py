from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from calc.forms import InvestmentForm
from calc.house import House, Mortgage, Investment
from decimal import Decimal

class InvestmentView(View): 
	
	form_class = InvestmentForm
	TERM_IN_YEARS = 30
	
	def buildInvestment(self):
		house = House(self.price, self.yearly_appreciation_rate, self.yearly_property_tax_rate, self.yearly_maintenance_as_percent_of_value, self.insurance)	
		mortgage = Mortgage(house, self.yearly_interest_rate, self.TERM_IN_YEARS, self.down_payment_percent)	
		investment = Investment(house, mortgage, self.closing_cost_as_percent_of_value, self.alternative_rent, self.realtor_cost, self.federal_tax_rate, self.state_tax_rate)
		return investment
	
	def getBaseStreamAndMortgagePayment(self):
		investment = self.buildInvestment()
		irr, cash_flows = investment.getYearlyCashFlowsAndIRR()
		mortgage_payment = int(round(investment.mortgage.getMonthlyPayment()))
		
		return irr, cash_flows, mortgage_payment
	
	def getModifiedIRR(self, irr_increment):
		appreciation_rate = self.yearly_appreciation_rate + irr_increment
		investment = self.buildInvestment()
		investment.house.yearly_appreciation_rate = appreciation_rate
		
		return investment.getYearlyCashFlowsAndIRR(irr_only=True)
	
	def getMortgageValueDriver(self, comparison_irr):
		house = House(self.price, self.yearly_appreciation_rate, self.yearly_property_tax_rate, self.yearly_maintenance_as_percent_of_value, self.insurance)	
		mortgage = Mortgage(house, 0, self.TERM_IN_YEARS, 1)	
		investment = Investment(house, mortgage, self.closing_cost_as_percent_of_value, self.alternative_rent, self.realtor_cost, self.federal_tax_rate, self.state_tax_rate)
		irr = investment.getYearlyCashFlowsAndIRR(irr_only=True)
		
		delta = self.getIRRDelta(comparison_irr, irr)
		return delta
	
	def getAlternativeRentValueDriver(self, comparison_irr):
		investment = self.buildInvestment()
		investment.alternative_rent = 0
		irr = investment.getYearlyCashFlowsAndIRR(irr_only=True)
		
		print(comparison_irr)
		print(irr)
		delta = self.getIRRDelta(comparison_irr, irr)
		print(delta)
		return delta
		
	def getIRRDelta(self, base_irr, alternative_irr):
		irr_delta = []
		for year in range(1,31):
			delta =  base_irr[year] - alternative_irr[year]
			irr_delta.append(round(delta,2))
		
		return irr_delta
		
	
	def get(self, request, *args, **kwargs):
		
		form = self.form_class(request.GET)
		if form.is_valid():			
			
			# House object fields
			self.price = form.cleaned_data['price']
			self.yearly_appreciation_rate = form.cleaned_data['yearly_appreciation']
			self.yearly_property_tax_rate = form.cleaned_data['property_tax']
			self.yearly_maintenance_as_percent_of_value = form.cleaned_data['maintenance_cost']
			self.insurance = form.cleaned_data['insurance']

			# Mortgage objects fields
			self.yearly_interest_rate = form.cleaned_data['interest_rate']
			self.down_payment_percent = form.cleaned_data['down_payment']
			
			# Investment object fields
			self.closing_cost_as_percent_of_value = form.cleaned_data['closing_cost']
			self.alternative_rent = form.cleaned_data['alternative_rent'] * 12
			self.realtor_cost = form.cleaned_data['realtor_cost']
			self.federal_tax_rate = form.cleaned_data['federal_tax_bracket']
			self.state_tax_rate = form.cleaned_data['state_tax_bracket']			
			
			# Base stream
			irr, cash_stream, mortgage_payment = self.getBaseStreamAndMortgagePayment()
			context_dict = {
				'base_irr': irr,
				'cash_stream': cash_stream,
				'mortgage_payment': mortgage_payment
			}
			
			# High stream
			HIGH_CASE_INCREASE = Decimal(.01)
			high_irr = self.getModifiedIRR(HIGH_CASE_INCREASE)
			context_dict['high_irr'] = high_irr
			
			# Low stream
			LOW_CASE_DECREASE = -Decimal(.01)
			low_irr = self.getModifiedIRR(LOW_CASE_DECREASE)
			context_dict['low_irr'] = low_irr
			
			context_dict['mortgage_driver_irr'] = self.getMortgageValueDriver(irr)
			context_dict['alternative_rent_driver_irr'] = self.getAlternativeRentValueDriver(irr)
			
			return JsonResponse(context_dict)
		else:
			print(form.errors)
		
		return JsonResponse(form.errors)

class IndexView(View): 

	template_name = 'calc/index.html'
	form_class = InvestmentForm
	
	def get(self, request, *args, **kwargs):
		
		float_parameters = ['closing_cost', 'maintenance_cost', 'property_tax', 'down_payment', 'interest_rate', 'yearly_appreciation', 'realtor_cost', 'federal_tax_bracket', 'state_tax_bracket', 'insurance']
		
		context_dict = {}
		
		for parameter in float_parameters:
			if parameter in request.GET:
				try:
					context_dict[parameter] = float(request.GET[parameter])
				except:
					pass
				
		int_parameters = ['price', 'alternative_rent']
		
		for parameter in int_parameters:
			if parameter in request.GET:
				try:
					context_dict[parameter] = int(request.GET[parameter])
				except:
					pass
				
		print(context_dict)
		
		return render(request, self.template_name, context_dict)