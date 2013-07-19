# -*- mode: ruby -*-
# vi: set ft=ruby :

python_version = "python2.7"

Vagrant::Config.run do |config|
  config.vm.define :box do |config|
    config.vm.box = "precise64"
    config.vm.box_url = "http://files.vagrantup.com/precise64.box"
    config.vm.host_name = "box"
    config.vm.forward_port 5002, 5002

    config.vm.provision :shell, :inline => "sudo apt-get -y update"
    config.vm.provision :shell, :inline => "sudo apt-get install -y python-software-properties"
    config.vm.provision :shell, :inline => "sudo apt-get update"
    config.vm.provision :shell, :inline => "sudo apt-get install -y " + python_version + " " + python_version + "-dev"
    config.vm.provision :shell, :inline => "sudo apt-get install -y python-pip"
    config.vm.provision :shell, :inline => "sudo apt-get install -y make git libpq-dev pandoc libjpeg-dev libzip-dev"
    config.vm.provision :shell, :inline => "sudo apt-get install -y libxml2-dev libxslt1-dev"

    config.vm.provision :shell, :inline => "pip install -r /vagrant/deps.txt"
  end
end
