// Script de debug para testar os dashboards Power BI
// Execute no console do navegador (F12) na página de análises

// Testar se o endpoint está funcionando
async function testDashboards() {
    try {
        console.log('🔍 Testando dashboards Power BI...');

        // Verificar se o usuário está logado
        const token = localStorage.getItem('access_token');
        if (!token) {
            console.error('❌ Nenhum token encontrado - usuário não está logado');
            return;
        }
        console.log('✅ Token encontrado');

        // Testar endpoint de debug
        const debugResponse = await fetch('http://localhost:8000/analyses/debug-user', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!debugResponse.ok) {
            console.error('❌ Erro na resposta de debug:', debugResponse.status);
            return;
        }

        const debugData = await debugResponse.json();
        console.log('📊 Dados do usuário:', debugData);

        // Testar endpoint de dashboards
        const dashboardsResponse = await fetch('http://localhost:8000/analyses/powerbi-dashboards', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!dashboardsResponse.ok) {
            console.error('❌ Erro na resposta de dashboards:', dashboardsResponse.status);
            return;
        }

        const dashboards = await dashboardsResponse.json();
        console.log('📈 Dashboards disponíveis:', dashboards);

        if (Object.keys(dashboards).length === 0) {
            console.warn('⚠️ Nenhum dashboard disponível para este usuário');
            console.log('Permissões do usuário:', debugData.permissions);
        } else {
            console.log('✅ Dashboards encontrados:', Object.keys(dashboards));
        }

    } catch (error) {
        console.error('❌ Erro no teste:', error);
    }
}

// Executar teste
testDashboards();
