import tensorflow as tf
import numpy as np

tf.enable_eager_execution()


execfile("definitions.py")

train_batch_size = 4
num_steps = 10
num_features = 512
state_size = 128

checkpoint_path_1 = "checkpoints/model"




RESTORE=True



with tf.device('/gpu:0'):

	RIM = RIM_CELL(train_batch_size , num_steps , num_features , state_size)



	IM_gen = Data_Generator(train_batch_size=train_batch_size,test_batch_size=train_batch_size)
	Phys_Mod_obj = Phys_Mod()

	physical_model = lens_util_obj.physical_model



	optimizer = tf.train.AdamOptimizer(1e-3)
    
    
	if (RESTORE==True):
		RIM.model_1.load_weights(checkpoint_path_1)


	noise_rms = 0.01
	IM_gen.draw_im("test")

	for train_iter in range(100):
	    #if ((train_iter%1)==0):
	    #	print train_iter
	    IM_gen.draw_im("train")
	    noisy_data = Phys_Mod_obj.simulate_noisy_lensed_image(  IM_gen.IM_tr[:,:,:,:],noise_rms)
	    tf_IM =  tf.identity(IM_gen.IM_tr[:,:,:,:])


	    with tf.GradientTape() as tape:
	        tape.watch(RIM.model_1.variables)
	        cost_value, os1 = RIM.cost_function(noisy_data, tf_IM)
	    weight_grads = tape.gradient(cost_value, RIM.model_1.variables )

	    clipped_grads_1 = [tf.clip_by_value(grads_i,-10,10) for grads_i in weight_grads[0]]
	    optimizer.apply_gradients(zip(clipped_grads_1, RIM.model_1.variables), global_step=tf.train.get_or_create_global_step())
	    print( train_iter , cost_value.numpy() )

        if (((train_iter+1)%100)==0):
                RIM.model_1.save_weights(checkpoint_path_1)
                print('saved weights.')

