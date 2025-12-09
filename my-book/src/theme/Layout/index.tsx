import React, { JSX } from 'react';
import Layout from '@theme-original/Layout';
import Chatbot from '../../components/Chatbot';

type LayoutProps = {
  children: React.ReactNode;
  [key: string]: any;
};

const LayoutWrapper = (props: LayoutProps): JSX.Element => {
  return (
    <>
      <Layout {...props}>
        {props.children}
      </Layout>
      <Chatbot />
    </>
  );
};

export default LayoutWrapper;