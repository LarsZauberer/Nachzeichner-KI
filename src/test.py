import argparse
from pathlib import Path
import logging

from data.ai_data import AI_Data
from modules.environment import Environment as Rep_Env
from modules.nn_agent import Agent as Rep_Agent

from extras.physics_modules.environment import Environment as Phy_Env
from extras.physics_modules.nn_agent import Agent as Phy_Agent

import numpy as np
    
from test_functions import test_env, generative_test_env

from extras.logger import critical, initialize_logging
from data_statistics.Image_Generator import generate_image, generate_generative_image



@critical
def physics_test(args):
    """
    physics_test tests a physics model

    :param args: Arguments from argparsing
    :type args: Namespace
    """
    log = logging.getLogger("Tester")

    #load data
    data = AI_Data(args.dataset)
    data.sample(args.test)

    # initialize environment
    canvas_size = 28
    patch_size = 5
    n_actions = 42
    glob_in_dims = (4, canvas_size, canvas_size)
    loc_in_dims = (2, patch_size, patch_size)
    
    env =  Phy_Env(canvas_size, patch_size, data.labeled_pro_data, n_actions=n_actions, friction=0.3, vel_1=0.9, vel_2=1.5, with_overdraw=True, dataset=args.dataset.split("_")[0])
    agent_args = {"gamma": 0, "epsilon_episodes": 1000, "epsilon": 0, "alpha": 0, "replace_target": 1000, 
                  "global_input_dims": glob_in_dims, "local_input_dims": loc_in_dims, 
                  "mem_size": 1000, "batch_size": 64, "n_actions": n_actions}
    agent = Phy_Agent(**agent_args)
    agent.load_models(f"pretrained_models/reproduce/{args.name}")

    log.info(f"Recognized a physics model")

    # Run Test
    scores = test_env(
        env=env,
        agent=agent,
        data=data,
        n_episodes=args.test,
        )
    
    # process Results
    images = scores.pop(-1)

    reward, accuracy, datarec, speed, drawratio, overdraw = [float('%.3f' % s) for s in scores]
    log.info(f'reward: {reward}, accuracy: {accuracy}, {data.dataset}-recognition: {datarec}, speed {speed}, drawratio: {drawratio}, overdrawn: {overdraw}')
    
    generate_image(images)

    with open(f"results/{args.name}-{args.dataset}", "w") as f:
        f.write(f'reward: {reward}, accuracy: {accuracy}, {data.dataset}-recognition: {datarec}, speed {speed}, drawratio: {drawratio}, overdrawn: {overdraw}')


@critical
def reproduce_test(args):
    """
    reproduce_test tests a reproduce model

    :param args: Arguments from argparsing
    :type args: Namespace
    """
    log = logging.getLogger("Tester")
    
    # load data
    data = AI_Data(args.dataset)
    data.sample(args.test)

    # initialize environment
    canvas_size = 28
    patch_size = 7
    env = Rep_Env(canvas_size, patch_size, data.labeled_pro_data, with_stopAction=True, with_overdraw=True, dataset=args.dataset.split("_")[0])
    agent_args = {"softmax": args.softmax, "gamma": 0, "epsilon_episodes": 1000, "epsilon": 0, "alpha": 0, "replace_target": 1000, 
                  "global_input_dims": (4, canvas_size, canvas_size), "local_input_dims": (2, patch_size, patch_size), 
                  "mem_size": 1000, "batch_size": 64}
    agent = Rep_Agent(**agent_args)
    agent.load_models(f"pretrained_models/reproduce/{args.name}")

    log.info(f"Recognized a reproduce model")

    # Run Test
    scores = test_env(
        env=env,
        agent=agent,
        data=data,
        n_episodes=args.test
        )

    #process Results
    images = scores.pop(-1)
    reward, accuracy, datarec, speed, drawratio, overdraw = [float('%.3f' % s) for s in scores]
    log.info(f'reward: {reward}, accuracy: {accuracy}, {data.dataset}-recognition: {datarec}, speed {speed}, drawratio: {drawratio}, overdrawn: {overdraw}')
    
    generate_image(images)

    with open(f"results/{args.name}-{args.dataset}", "w") as f:
        f.write(f'reward: {reward}, accuracy: {accuracy}, {data.dataset}-recognition: {datarec}, speed {speed}, drawratio: {drawratio}, overdrawn: {overdraw}')



@critical
def generative_test(args):
    """
    reproduce_test tests a reproduce model

    :param args: Arguments from argparsing
    :type args: Namespace
    """
    log = logging.getLogger("Tester")
    
    # initialize environment
    canvas_size = 28
    patch_size = 7
    env = Rep_Env(canvas_size, patch_size, referenceData=np.full((args.test, 28, 28), 1), generative=True, with_stopAction=True, with_noisy=args.noisyPixel, dataset=args.dataset.split("_")[0])
    env.label = int(args.genMotive)

    agent_args = {"softmax": args.softmax, "gamma": 0, "epsilon_episodes": 1000, "epsilon": 0, "alpha": 0, "replace_target": 1000, 
                  "global_input_dims": (4, canvas_size, canvas_size), "local_input_dims": (2, patch_size, patch_size), 
                  "mem_size": 1000, "batch_size": 64}
    agent = Rep_Agent(**agent_args)
    agent.load_models(f"pretrained_models/generative/{args.name}")

    log.info(f"Recognized a generative model")

    # adjustable softmax temperature
    agent.set_softmax_temp(0.2)
 
    # Run Test
    scores = generative_test_env(
        env=env,
        agent=agent,
        n_episodes=args.test
        )

    # process Results
    images = scores.pop(-1)
    datarec, speed, drawratio = [float('%.3f' % s) for s in scores]
    log.info(f'mnist-recognition: {datarec}, speed: {speed}, drawratio: {drawratio}' )
    
    generate_generative_image(images)

    with open(f"results/{args.name}-{args.dataset}", "w") as f:
        f.write(f"recognition: {datarec}, speed {speed}, drawratio: {drawratio}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", help="Number of test episodes", action="store", type=int, default=100)
    parser.add_argument("-d", "--dataset", help="Name of the dataset to run the test on", action="store", type=str, default="mnist_test")
    parser.add_argument("-n", "--name", help="The version to test", action="store", type=str, default="base-base")
    parser.add_argument("-p", "--physics", help="Run the physics version", action="store_true", default=False)
    parser.add_argument("-g", "--generative", help="Run the Generative version", action="store_true", default=False)
    parser.add_argument("-sm", "--softmax", help="Run the NN with Softmax activation", action="store_true", default=False)
    parser.add_argument("-np", "--noisyPixel", help="Run the NoisyPixel version", action="store_true", default=False)
    parser.add_argument("-gm", "--genMotive", help="generative Motive", action="store", default=2)
    parser.add_argument("--debug", help="Verbose for the logging", action="store_true", default=False)
    args = parser.parse_args()
    
    initialize_logging(args)
    log = logging.getLogger()
    
    # Print all the configuration
    log.info(f"Number of test episodes: {args.test}")
    log.info(f"Dataset: {args.dataset}")
    log.info(f"Model Name: {args.name}")
    log.info(f"softmax: {args.softmax}")

    #run tests
    if args.physics:
        physics_test(args)
    elif args.generative:
        generative_test(args)
    else:
        reproduce_test(args)












    

    
