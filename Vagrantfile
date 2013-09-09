# -*- mode: ruby -*-
# vi: set ft=ruby :

python_version = "python2.7"

Vagrant::Config.run do |config|
  config.vm.define :box do |config|
    config.ssh.username = "vagrant"

    config.vm.box = "precise64"
    config.vm.box_url = "http://files.vagrantup.com/precise64.box"
    config.vm.host_name = "owf2013"
    config.vm.forward_port 80, 8080

    config.vm.provision :salt do |salt|
      salt.minion_config = "salt/minion.conf"
      salt.run_highstate = true
      salt.salt_install_type = "stable"
    end
  end
end
