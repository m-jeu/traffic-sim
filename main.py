import trafficsim

if __name__ == "__main__":
    model_choice = None
    while model_choice not in ['1', '2']:
        model_choice = input('Number of lanes (1 or 2): ')
    trafficsim.launch_gui(multi_lane=False if model_choice == '1' else True)
