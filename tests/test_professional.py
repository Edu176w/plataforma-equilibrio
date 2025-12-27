import unittest
import numpy as np
from app.thermodynamics.professional_elv import ProfessionalELVCalculator
from app.utils.component_database import ComponentDatabase

class TestComponentDatabase(unittest.TestCase):
    '''Testes para banco de dados de componentes'''
    
    def setUp(self):
        self.db = ComponentDatabase()
    
    def test_search_water(self):
        '''Testar busca de água'''
        chem = self.db.search_component('Water')
        self.assertIsNotNone(chem)
        self.assertEqual(chem.CAS, '7732-18-5')
    
    def test_search_ethanol(self):
        '''Testar busca de etanol'''
        chem = self.db.search_component('Ethanol')
        self.assertIsNotNone(chem)
        self.assertAlmostEqual(chem.MW, 46.069, places=2)
    
    def test_get_properties(self):
        '''Testar obtenção de propriedades'''
        props = self.db.get_component_properties('Water')
        self.assertIn('name', props)
        self.assertIn('Tc', props)
        self.assertIn('Pc', props)
        self.assertGreater(props['Tc'], 600)  # Tc da água > 600 K
    
    def test_antoine_coefficients(self):
        '''Testar coeficientes de Antoine'''
        antoine = self.db.get_antoine_coefficients('Water')
        if antoine:
            self.assertIn('A', antoine)
            self.assertIn('B', antoine)
            self.assertIn('C', antoine)

class TestProfessionalELV(unittest.TestCase):
    '''Testes para calculadora profissional de ELV'''
    
    def setUp(self):
        self.components = ['Water', 'Ethanol']
        self.calc = ProfessionalELVCalculator(self.components, model='PR')
    
    def test_initialization(self):
        '''Testar inicialização'''
        self.assertEqual(len(self.calc.chemicals), 2)
        self.assertEqual(self.calc.model_type, 'PR')
    
    def test_bubble_point_pressure(self):
        '''Testar cálculo de ponto de bolha (P)'''
        T = 353.15  # 80°C
        xs = [0.5, 0.5]
        
        result = self.calc.calculate_bubble_point_P(T, xs)
        
        self.assertIn('P', result)
        self.assertIn('ys', result)
        self.assertGreater(result['P'], 0)
        self.assertAlmostEqual(sum(result['ys']), 1.0, places=5)
    
    def test_bubble_point_temperature(self):
        '''Testar cálculo de ponto de bolha (T)'''
        P = 101325  # 1 atm
        xs = [0.5, 0.5]
        
        result = self.calc.calculate_bubble_point_T(P, xs)
        
        self.assertIn('T', result)
        self.assertIn('ys', result)
        self.assertGreater(result['T'], 273.15)
        self.assertLess(result['T'], 373.15)
    
    def test_flash_calculation(self):
        '''Testar cálculo de flash'''
        T = 353.15
        P = 101325
        zs = [0.5, 0.5]
        
        result = self.calc.calculate_flash(T, P, zs)
        
        self.assertIn('beta', result)
        self.assertIn('xs', result)
        self.assertIn('ys', result)
        self.assertGreaterEqual(result['beta'], 0.0)
        self.assertLessEqual(result['beta'], 1.0)
    
    def test_pxy_diagram(self):
        '''Testar geração de diagrama P-xy'''
        T = 353.15
        
        result = self.calc.generate_Pxy_diagram(T, n_points=10)
        
        self.assertIn('P_bubble', result)
        self.assertIn('x', result)
        self.assertIn('y', result)
        self.assertEqual(len(result['x']), 10)
    
    def test_txy_diagram(self):
        '''Testar geração de diagrama T-xy'''
        P = 101325
        
        result = self.calc.generate_Txy_diagram(P, n_points=10)
        
        self.assertIn('T_bubble', result)
        self.assertIn('x', result)
        self.assertIn('y', result)
        self.assertEqual(len(result['x']), 10)

class TestDataValidation(unittest.TestCase):
    '''Testes de validação com dados experimentais'''
    
    def test_water_vapor_pressure_at_100C(self):
        '''Testar pressão de vapor da água a 100°C (deve ser ~101325 Pa)'''
        db = ComponentDatabase()
        chem = db.search_component('Water')
        
        P_sat = chem.VaporPressure(373.15)
        
        # Deve ser próximo de 1 atm (101325 Pa)
        self.assertAlmostEqual(P_sat, 101325, delta=1000)
    
    def test_ethanol_vapor_pressure_at_78C(self):
        '''Testar pressão de vapor do etanol a 78°C (ponto de ebulição)'''
        db = ComponentDatabase()
        chem = db.search_component('Ethanol')
        
        P_sat = chem.VaporPressure(351.44)  # Tb do etanol
        
        # Deve ser próximo de 1 atm
        self.assertAlmostEqual(P_sat, 101325, delta=2000)

def run_all_tests():
    '''Executar todos os testes'''
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestComponentDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestProfessionalELV))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == '__main__':
    print('='*70)
    print('TESTES UNITÁRIOS - PLATAFORMA DE EQUILÍBRIO DE FASES')
    print('='*70)
    print()
    
    result = run_all_tests()
    
    print()
    print('='*70)
    print(f'Total de testes: {result.testsRun}')
    print(f'Sucessos: {result.testsRun - len(result.failures) - len(result.errors)}')
    print(f'Falhas: {len(result.failures)}')
    print(f'Erros: {len(result.errors)}')
    print('='*70)
