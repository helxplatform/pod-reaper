import os
import sys

import logger
from pytz import utc
from time import sleep
from datetime import datetime, timedelta

from options import Options
from check_rules import RulesLoader

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from kubernetes import client as k8s_client, config as k8s_config

logger = logger.get_logger(__name__)


class Reaper:

    def __init__(self):

        try:
            if os.getenv('KUBERNETES_SERVICE_HOST'):
                k8s_config.load_incluster_config()
            else:
                k8s_config.load_kube_config()
            logger.info("Kube config loaded.")
            api_client = k8s_client.ApiClient()
            self.options = Options.load_options()
            self.api = k8s_client.CoreV1Api(api_client)
            self.apps_api = k8s_client.AppsV1Api(api_client)
            self.rules_loader = RulesLoader()
            self.loaded_rules = self.rules_loader.load_rules()

        except Exception as e:
            logger.exception(f"Exception occurred when loading Options and K8s APIs. {e}")
            sys.exit()

    def harvest(self):
        """Main process to reap the pods based on labels and pod_rules"""

        run_forever = float(self.options.run_duration) == 0
        logger.info(f"Running pod reaper indefinitely: {run_forever}")

        if run_forever:
            scheduler = BlockingScheduler(timezone=utc)
            scheduler.add_job(self.scythe_cycle, 'interval', seconds=int(self.options.schedule))
            scheduler.start()

        if not run_forever:
            scheduler = BackgroundScheduler(timezone=utc)
            end_date_obj = datetime.now() + timedelta(minutes=int(self.options.run_duration * 60))
            job = scheduler.add_job(self.scythe_cycle, 'interval', seconds=int(self.options.schedule))
            scheduler.start()

            while True:
                if datetime.now() > end_date_obj:
                    job.remove()
                    scheduler.shutdown()
                    break
                else:
                    sleep(2)

    def scythe_cycle(self):
        deployments_list = self.get_deployments_list()

        for deployment in deployments_list:
            resp = self.rules_loader.should_reap(deployment)
            if resp:
                deployment_name = deployment.metadata.name
                logger.info(f"Reaping Pods associated to deployment: {deployment_name}")
                self.reap_pod(deployment_name)

    def get_deployments_list(self):
        """Generate a list of Deployment names that are filtered based on key-value pairs specified"""

        replica_sets_list = []
        pods_list = []
        deployments_list = []
        namespace = self.options.namespace

        label_strings = self.form_pod_label_strings(self.options.required_keys_values)

        for l_string in label_strings:
            pods = self.api.list_namespaced_pod(namespace=namespace, label_selector=l_string).items
            for pod in pods:
                if pod not in pods_list:
                    pods_list.append(pod)

        for item in pods_list:
            if item.metadata.owner_references[0].kind == "ReplicaSet":
                replica_set_name = item.metadata.owner_references[0].name
                if replica_set_name not in replica_sets_list:
                    replica_sets_list.append(replica_set_name)

        for replica_sets in replica_sets_list:
            replica_sets = self.apps_api.list_namespaced_replica_set(
                namespace=self.options.namespace,
                field_selector=f'metadata.name={replica_sets}'
            )
            rsets_items = replica_sets.items
            if len(rsets_items) == 1:
                name = rsets_items[0].metadata.owner_references[0].name
                resp = self.apps_api.read_namespaced_deployment(
                    name=name,
                    namespace=self.options.namespace
                )
                if resp:
                    deployments_list.append(resp)
        return deployments_list

    def form_pod_label_strings(self, keys_values):
        """Helper function to examine a pod contains labels with corresponding key and values"""

        l_strings = []
        for key, values in keys_values.items():
            for value in values:
                l_strings.append(f"{key}={value}")

        return l_strings

    def reap_pod(self, deployment_name):
        """Delete the deployment and the pod service"""

        _ = self.apps_api.delete_namespaced_deployment(
            name=deployment_name,
            namespace=self.options.namespace
        )
        logger.info(f"Successfully reaped the pods associated to deployment: {deployment_name}")
