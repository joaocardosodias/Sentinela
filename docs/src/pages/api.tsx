import React from 'react';
import Layout from '@theme/Layout';

export default function ApiDoc() {
  return (
    <Layout title="API Swagger" description="Documentação interativa da API">
      <div style={{ width: '100%', height: 'calc(100vh - 60px)' }}>
        <iframe 
          src="/swagger-ui.html" 
          style={{ width: '100%', height: '100%', border: 'none', backgroundColor: '#ffffff' }} 
          title="Swagger UI"
        />
      </div>
    </Layout>
  );
}
