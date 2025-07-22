"""
AWS Auto Scaling Group integration for host discovery.
"""
import logging
from typing import List, NamedTuple, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError


logger = logging.getLogger(__name__)


class InstanceInfo(NamedTuple):
    """Information about an ASG instance."""
    instance_id: str
    private_ip: str
    state: str
    hostname: str


class ASGClient:
    """AWS Auto Scaling Group client for host discovery."""

    def __init__(self, region_name: Optional[str] = None):
        """
        Initialize ASG client.
        
        Args:
            region_name: AWS region (uses default if not specified)
        """
        self.region_name = region_name
        try:
            self.session = boto3.Session()
            self.asg_client = self.session.client('autoscaling', region_name=region_name)
            self.ec2_client = self.session.client('ec2', region_name=region_name)
            
            # Test connection
            self.asg_client.describe_auto_scaling_groups(MaxRecords=1)
            region_msg = f" in region {region_name}" if region_name else ""
            logger.info(f"Successfully connected to AWS using IAM role{region_msg}")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {e}")
            raise

    def get_asg_instances(self, asg_name: str) -> List[InstanceInfo]:
        """
        Get instances from an Auto Scaling Group.
        
        Args:
            asg_name: Name of the Auto Scaling Group
            
        Returns:
            List of InstanceInfo objects
        """
        try:
            logger.info(f"Retrieving instances from ASG: {asg_name}")
            
            # Get ASG details
            response = self.asg_client.describe_auto_scaling_groups(
                AutoScalingGroupNames=[asg_name]
            )
            
            if not response['AutoScalingGroups']:
                raise ValueError(f"Auto Scaling Group '{asg_name}' not found")
            
            asg = response['AutoScalingGroups'][0]
            instance_ids = [instance['InstanceId'] for instance in asg['Instances']]
            
            if not instance_ids:
                logger.warning(f"No instances found in ASG: {asg_name}")
                return []
            
            # Get instance details
            ec2_response = self.ec2_client.describe_instances(
                InstanceIds=instance_ids
            )
            
            instances = []
            for reservation in ec2_response['Reservations']:
                for instance in reservation['Instances']:
                    instance_info = InstanceInfo(
                        instance_id=instance['InstanceId'],
                        private_ip=instance.get('PrivateIpAddress', ''),
                        state=instance['State']['Name'],
                        hostname=instance.get('PrivateDnsName', instance.get('PrivateIpAddress', ''))
                    )
                    instances.append(instance_info)
                    
                    if instance_info.state != 'running':
                        logger.warning(
                            f"Instance {instance_info.instance_id} is in state '{instance_info.state}'"
                        )
            
            logger.info(f"Found {len(instances)} instances in ASG {asg_name}")
            return instances
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS API error getting ASG instances: {error_code} - {error_message}")
            raise
        except BotoCoreError as e:
            logger.error(f"AWS connection error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting ASG instances: {e}")
            raise

    def get_running_hostnames(self, asg_name: str) -> List[str]:
        """
        Get hostnames of running instances from an ASG.
        
        Args:
            asg_name: Name of the Auto Scaling Group
            
        Returns:
            List of hostnames (private DNS names or IPs) for running instances
        """
        instances = self.get_asg_instances(asg_name)
        running_hostnames = [
            instance.hostname 
            for instance in instances 
            if instance.state == 'running' and instance.hostname
        ]
        
        logger.info(f"Found {len(running_hostnames)} running instances in ASG {asg_name}")
        return running_hostnames 