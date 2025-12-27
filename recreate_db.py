from app import create_app, db
from app.models import User, Simulation

app = create_app()

with app.app_context():
    # Dropar tudo e recriar
    db.drop_all()
    db.create_all()
    print('✅ Banco de dados recriado com sucesso!')
    
    # Adicionar simulação de exemplo
    from datetime import datetime
    import json
    
    example_sim = Simulation(
        module='elv',
        calculation_type='bubble',
        model='PR',
        components=json.dumps(['Water', 'Ethanol']),
        conditions=json.dumps({'temperature': 353.15, 'x': [0.5, 0.5]}),
        results=json.dumps({'P': 101325, 'ys': [0.3, 0.7]}),
        execution_time=0.25,
        success=True
    )
    
    db.session.add(example_sim)
    db.session.commit()
    
    print('✅ Simulação de exemplo adicionada!')
    print('✅ Total de simulações:', Simulation.query.count())
