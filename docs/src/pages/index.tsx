import {Redirect} from '@docusaurus/router';
import {useBaseUrlUtils} from '@docusaurus/useBaseUrl';

export default function Home(): JSX.Element {
  const {withBaseUrl} = useBaseUrlUtils();
  return <Redirect to={withBaseUrl('/solucao/')} />;
}
