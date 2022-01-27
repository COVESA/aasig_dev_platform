[Go to the previous page](../README.md)

----

This page is the example automation project, which was made with paf automation framework.

Visit [scenarios.xml](./scenarios.xml) to look at the declared phases, scenarios and parameters.

Visit [general.py](./general.py), [uboot.py](./uboot.py), [busybox.py](./busybox.py), [linux_kernel.py](./linux_kernel.py) to find implementation of specific tasks.

Use the following command to execute the main scenario:

```bash
# call below from the root paf folder
python ./paf_main.py -imd ./linux_deployment -c ./linux_deployment/scenarios.xml -s boot_image_deploy -p ARCH_TYPE=ARM -ld="./"
```

In order to change the executed scenario, phase or task, select the corresponding element from the [scenarios.xml](./scenarios.xml) and run the above command with slightly changed parameters.

----

[Go to the previous page](../README.md)
