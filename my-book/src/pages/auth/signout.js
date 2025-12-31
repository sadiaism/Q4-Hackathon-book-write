import React, { useEffect } from 'react';
import Layout from '@theme/Layout';
import { useHistory } from '@docusaurus/router';
import { signOut } from '../../utils/auth';

export default function SignoutPage() {
  const history = useHistory();

  useEffect(() => {
    signOut();
    // Redirect to home after signing out
    setTimeout(() => {
      history.push('/');
    }, 1000);
  }, [history]);

  return (
    <Layout title="Signing Out" description="You are being signed out">
      <div className="container margin-vert--lg">
        <div className="row">
          <div className="col col--6 col--offset-3">
            <div className="text--center padding--vert--xl">
              <h2>Signing Out</h2>
              <p>You are being signed out. Redirecting to home...</p>
              <div className="loading loading--sm margin-top--md"></div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}